"""
Tests for admin auth dependency and state manager – Phase 11.

Run from backend/ directory:
    python -m pytest tests/ -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from unittest.mock import patch

import core.config as cfg


class TestStateManager(unittest.TestCase):
    def setUp(self) -> None:
        # Reset singleton before each test.
        import services.state_manager as sm
        sm._state = None
        self._sm = sm

    def test_initial_state_matches_config(self) -> None:
        state = self._sm.get_state()
        self.assertEqual(state.prediction_mode, cfg.PREDICTION_MODE)
        self.assertEqual(state.monthly_rate_inr, cfg.DEFAULT_MONTHLY_RATE_INR)

    def test_update_prediction_mode(self) -> None:
        self._sm.get_state()
        updated = self._sm.update_state(prediction_mode="ai")
        self.assertEqual(updated.prediction_mode, "ai")

    def test_invalid_prediction_mode_raises(self) -> None:
        self._sm.get_state()
        with self.assertRaises(ValueError):
            self._sm.update_state(prediction_mode="quantum")

    def test_update_monthly_rate(self) -> None:
        self._sm.get_state()
        updated = self._sm.update_state(monthly_rate_inr=200_000)
        self.assertEqual(updated.monthly_rate_inr, 200_000)

    def test_zero_monthly_rate_raises(self) -> None:
        self._sm.get_state()
        with self.assertRaises(ValueError):
            self._sm.update_state(monthly_rate_inr=0)

    def test_negative_monthly_rate_raises(self) -> None:
        self._sm.get_state()
        with self.assertRaises(ValueError):
            self._sm.update_state(monthly_rate_inr=-1)

    def test_update_ai_profile(self) -> None:
        self._sm.get_state()
        updated = self._sm.update_state(ai_profile="conservative")
        self.assertEqual(updated.ai_profile, "conservative")

    def test_invalid_ai_profile_raises(self) -> None:
        self._sm.get_state()
        with self.assertRaises(ValueError):
            self._sm.update_state(ai_profile="reckless")

    def test_update_currency_uppercased(self) -> None:
        self._sm.get_state()
        updated = self._sm.update_state(default_currency="usd")
        self.assertEqual(updated.default_currency, "USD")

    def test_partial_update_preserves_other_fields(self) -> None:
        self._sm.get_state()
        self._sm.update_state(prediction_mode="ai")
        self._sm.update_state(monthly_rate_inr=200_000)
        state = self._sm.get_state()
        self.assertEqual(state.prediction_mode, "ai")
        self.assertEqual(state.monthly_rate_inr, 200_000)


class TestAdminAuth(unittest.TestCase):
    """
    Tests for admin_auth.require_admin_key dependency.

    We test the auth logic directly (not via HTTP) by calling the
    function with mock credentials objects.
    """

    def _make_creds(self, token: str):
        from fastapi.security import HTTPAuthorizationCredentials
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    def test_valid_token_passes(self) -> None:
        from fastapi import HTTPException
        import services.admin_auth as auth

        with patch.dict(os.environ, {"ADMIN_API_KEY": "secret123"}):
            # Should not raise.
            try:
                auth.require_admin_key(self._make_creds("secret123"))
            except HTTPException:
                self.fail("require_admin_key raised HTTPException with valid token")

    def test_wrong_token_raises_401(self) -> None:
        from fastapi import HTTPException
        import services.admin_auth as auth

        with patch.dict(os.environ, {"ADMIN_API_KEY": "secret123"}):
            with self.assertRaises(HTTPException) as ctx:
                auth.require_admin_key(self._make_creds("wrong"))
            self.assertEqual(ctx.exception.status_code, 401)

    def test_missing_credentials_raises_401(self) -> None:
        from fastapi import HTTPException
        import services.admin_auth as auth

        with patch.dict(os.environ, {"ADMIN_API_KEY": "secret123"}):
            with self.assertRaises(HTTPException) as ctx:
                auth.require_admin_key(None)
            self.assertEqual(ctx.exception.status_code, 401)

    def test_missing_env_key_raises_503(self) -> None:
        from fastapi import HTTPException
        import services.admin_auth as auth

        with patch.dict(os.environ, {}, clear=True):
            # Ensure ADMIN_API_KEY is absent.
            os.environ.pop("ADMIN_API_KEY", None)
            with self.assertRaises(HTTPException) as ctx:
                auth.require_admin_key(self._make_creds("anything"))
            self.assertEqual(ctx.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
