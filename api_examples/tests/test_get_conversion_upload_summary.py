# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import unittest
from unittest.mock import MagicMock, call
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.client import GoogleAdsClient
from api_examples.get_conversion_upload_summary import main


class TestGetConversionUploadSummary(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=GoogleAdsClient)
        self.mock_ga_service = MagicMock()
        self.mock_client.get_service.return_value = self.mock_ga_service
        self.customer_id = "1234567890"

        self.captured_output = StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_main_success(self):
        # Mock responses for search_stream
        mock_batch_1 = MagicMock()
        mock_row_1 = MagicMock()
        mock_summary_1 = MagicMock()
        mock_summary_1.resource_name = "customers/123/offlineConversionUploadClientSummaries/1"
        mock_summary_1.status.name = "SUCCESS"
        mock_summary_1.total_event_count = 10
        mock_summary_1.successful_event_count = 10
        mock_summary_1.success_rate = 1.0
        mock_summary_1.last_upload_date_time = "2024-01-01 12:00:00"
        mock_summary_1.alerts = []
        mock_summary_1.daily_summaries = []
        mock_summary_1.job_summaries = []
        mock_row_1.offline_conversion_upload_client_summary = mock_summary_1
        mock_batch_1.results = [mock_row_1]

        mock_batch_2 = MagicMock()
        mock_row_2 = MagicMock()
        mock_summary_2 = MagicMock()
        mock_summary_2.resource_name = "customers/123/offlineConversionUploadConversionActionSummaries/1"
        mock_summary_2.conversion_action_name = "My Conversion Action"
        mock_summary_2.status.name = "SUCCESS"
        mock_summary_2.total_event_count = 5
        mock_summary_2.successful_event_count = 5
        mock_summary_2.alerts = []
        mock_summary_2.daily_summaries = []
        mock_summary_2.job_summaries = []
        mock_row_2.offline_conversion_upload_conversion_action_summary = mock_summary_2
        mock_batch_2.results = [mock_row_2]

        # The first call returns client summary, second call returns conversion action summary
        self.mock_ga_service.search_stream.side_effect = [[mock_batch_1], [mock_batch_2]]

        main(self.mock_client, self.customer_id)

        # Check output
        output = self.captured_output.getvalue()
        self.assertIn("Offline Conversion Upload Client Summary:", output)
        self.assertIn("Resource Name: customers/123/offlineConversionUploadClientSummaries/1", output)
        self.assertIn("Offline Conversion Upload Conversion Action Summary:", output)
        self.assertIn("Conversion Action Name: My Conversion Action", output)

        self.assertEqual(self.mock_ga_service.search_stream.call_count, 2)

    def test_main_google_ads_exception(self):
        mock_error = MagicMock()
        mock_error.code.return_value.name = "INTERNAL_ERROR"
        mock_failure = MagicMock()
        mock_failure.errors = [MagicMock(message="Internal error")]
        
        self.mock_ga_service.search_stream.side_effect = GoogleAdsException(
            error=mock_error,
            call=MagicMock(),
            failure=mock_failure,
            request_id="test_request_id"
        )

        with self.assertRaises(SystemExit) as cm:
            main(self.mock_client, self.customer_id)
        
        self.assertEqual(cm.exception.code, 1)
        output = self.captured_output.getvalue()
        self.assertIn('Request with ID "test_request_id" failed with status "INTERNAL_ERROR"', output)

if __name__ == "__main__":
    unittest.main()
