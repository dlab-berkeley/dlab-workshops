"""Regression coverage for failed imports replacing valid workshop data."""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from googleapiclient.errors import HttpError
from httplib2 import Response


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCRIPTS = [load_script('fetch_google_sheets'), load_script('fetch_workshop_catalog')]


class SheetImportTests(unittest.TestCase):
    def test_permission_errors_exit_nonzero_and_preserve_all_data(self):
        for script in SCRIPTS:
            with self.subTest(script=script.__name__), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                paths = [root / '_data/upcoming_workshops.json',
                         root / 'data/upcoming_workshops.json', root / '_data/workshops.yml']
                for path in paths:
                    path.parent.mkdir(exist_ok=True)
                    path.write_text('last valid data')
                service = Mock()
                service.spreadsheets.return_value.values.return_value.get.return_value.execute.side_effect = HttpError(
                    Response({'status': '403'}), b'{"error":{"message":"The caller does not have permission"}}')
                with patch.object(script, '__file__', str(root / 'scripts/import.py')), \
                     patch.object(script, 'get_google_sheets_service', return_value=service), \
                     patch.dict(os.environ, {'GOOGLE_SHEET_ID': 'sessions', 'GOOGLE_WORKSHOPS_SHEET_ID': 'catalog'}):
                    with self.assertRaises(SystemExit) as result:
                        script.main()
                self.assertEqual(result.exception.code, 1)
                self.assertEqual([p.read_text() for p in paths], ['last valid data'] * 3)

    def test_missing_or_invalid_credentials_fail(self):
        for script in SCRIPTS:
            for env in [{}, {'GOOGLE_SERVICE_ACCOUNT_KEY': 'not json'}]:
                with self.subTest(script=script.__name__, env=env), patch.dict(os.environ, env, clear=True):
                    with self.assertRaises(RuntimeError):
                        script.fetch_google_sheet_data('sheet')

    def test_empty_or_wrong_sheet_is_an_error(self):
        for script in SCRIPTS:
            for values in [[], [['wrong_column'], ['value']]]:
                with self.subTest(script=script.__name__, values=values):
                    service = Mock()
                    service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {'values': values}
                    with patch.object(script, 'get_google_sheets_service', return_value=service):
                        with self.assertRaises(RuntimeError):
                            script.fetch_google_sheet_data('sheet')

    def test_valid_empty_schedule_updates_both_json_files(self):
        script = SCRIPTS[0]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            service = Mock()
            service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
                'values': [['evsprk__Event_Title__c', 'evsprk__Start_Date__c', 'evsprk__Stage__c']]}
            with patch.object(script, '__file__', str(root / 'scripts/import.py')), \
                 patch.object(script, 'get_google_sheets_service', return_value=service), \
                 patch.dict(os.environ, {'GOOGLE_SHEET_ID': 'sessions'}):
                script.main()
            internal = json.loads((root / '_data/upcoming_workshops.json').read_text())
            public = json.loads((root / 'data/upcoming_workshops.json').read_text())
            self.assertEqual(internal, public)
            self.assertEqual(public['workshops'], [])
            self.assertEqual(public['total_workshops'], 0)


if __name__ == '__main__':
    unittest.main()
