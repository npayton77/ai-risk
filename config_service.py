#!/usr/bin/env python3
"""
Centralized configuration service for YAML-driven settings.
Loads questions, flexible scoring, legacy scoring (for compatibility),
and recommendations. Provides mtime-based reload to reflect admin edits
without restarting the app.
"""

import os
import threading
import yaml
from typing import Dict, Any
from questions_loader import QuestionsLoader


class ConfigService:
    def __init__(
        self,
        questions_dir: str = 'questions',
        scoring_flexible_path: str = 'scoring_flexible.yaml',
        recommendations_path: str = 'recommendations.yaml',
        legacy_scoring_path: str = 'scoring.yaml'
    ) -> None:
        self.questions_dir = questions_dir
        self.scoring_flexible_path = scoring_flexible_path
        self.recommendations_path = recommendations_path
        self.legacy_scoring_path = legacy_scoring_path

        self._lock = threading.Lock()
        self._questions_loader = QuestionsLoader(self.questions_dir)

        # Cached configs
        self._questions_config: Dict[str, Any] = {}
        self._flexible_scoring: Dict[str, Any] = {}
        self._recommendations: Dict[str, Any] = {}
        self._legacy_scoring: Dict[str, Any] = {}

        # mtimes
        self._mtimes: Dict[str, float] = {}

        self._load_all(force=True)

    def _safe_load_yaml(self, path: str) -> Dict[str, Any]:
        try:
            if not os.path.exists(path):
                return {}
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def _dir_latest_mtime(self, directory: str) -> float:
        try:
            mtimes = [
                os.path.getmtime(os.path.join(directory, f))
                for f in os.listdir(directory)
                if f.endswith('.yaml')
            ]
            return max(mtimes) if mtimes else 0.0
        except Exception:
            return 0.0

    def _load_all(self, force: bool = False) -> None:
        with self._lock:
            # Questions
            if force or self._has_questions_changed():
                self._questions_loader = QuestionsLoader(self.questions_dir)
                self._questions_config = self._questions_loader.load_all_questions()
                self._mtimes['questions_dir'] = self._dir_latest_mtime(self.questions_dir)

            # Flexible scoring
            if force or self._has_changed('scoring_flexible', self.scoring_flexible_path):
                self._flexible_scoring = self._safe_load_yaml(self.scoring_flexible_path)
                self._mtimes['scoring_flexible'] = self._file_mtime(self.scoring_flexible_path)

            # Recommendations
            if force or self._has_changed('recommendations', self.recommendations_path):
                self._recommendations = self._safe_load_yaml(self.recommendations_path)
                self._mtimes['recommendations'] = self._file_mtime(self.recommendations_path)

            # Legacy scoring
            if force or self._has_changed('legacy_scoring', self.legacy_scoring_path):
                self._legacy_scoring = self._safe_load_yaml(self.legacy_scoring_path)
                self._mtimes['legacy_scoring'] = self._file_mtime(self.legacy_scoring_path)

    def _file_mtime(self, path: str) -> float:
        try:
            return os.path.getmtime(path) if os.path.exists(path) else 0.0
        except Exception:
            return 0.0

    def _has_changed(self, key: str, path: str) -> bool:
        current = self._file_mtime(path)
        return current != self._mtimes.get(key, -1.0)

    def _has_questions_changed(self) -> bool:
        current = self._dir_latest_mtime(self.questions_dir)
        return current != self._mtimes.get('questions_dir', -1.0)

    # Public API
    def reload_if_changed(self) -> None:
        self._load_all(force=False)

    def get_questions_config(self) -> Dict[str, Any]:
        return self._questions_config

    def get_flexible_scoring(self) -> Dict[str, Any]:
        return self._flexible_scoring

    def get_recommendations(self) -> Dict[str, Any]:
        return self._recommendations

    def get_legacy_scoring(self) -> Dict[str, Any]:
        return self._legacy_scoring

    # Helpers commonly needed
    def get_dimension_config(self) -> Dict[str, Any]:
        return self._flexible_scoring.get('dimensions', {})

    def get_risk_thresholds(self) -> Dict[str, Any]:
        return self._flexible_scoring.get('risk_thresholds', {})

    def get_risk_styling(self) -> Dict[str, Any]:
        if 'risk_styling' in self._flexible_scoring:
            return self._flexible_scoring['risk_styling']
        legacy = self._legacy_scoring or {}
        return legacy.get('risk_styling', {})

    def get_legacy_dimensions(self) -> Dict[str, Dict[str, int]]:
        legacy = self._legacy_scoring or {}
        return legacy.get('scoring', {}).get('dimensions', {})


# Global instance for convenience
config_service = ConfigService()


