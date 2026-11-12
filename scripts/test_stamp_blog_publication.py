from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

spec = spec_from_file_location('publication_stamp', Path(__file__).with_name('stamp-blog-publication.py'))
module = module_from_spec(spec)
spec.loader.exec_module(module)


class PublicationStampTests(unittest.TestCase):
    def test_preserves_original_dates_and_body_and_replaces_one_timestamp(self):
        original = '---\npubDate: "2026-10-05"\nupdatedDate: "2026-10-22"\n---\n\n文章\n'
        at = datetime(2026, 10, 22, 15, 0, tzinfo=timezone.utc)
        once = module.stamp_publication(original, at)
        self.assertEqual(module.stamp_publication(once, at), once)
        self.assertIn('pubDate: "2026-10-05"', once)
        self.assertIn('updatedDate: "2026-10-22"', once)
        self.assertIn('lastPublishedAt: "2026-10-22T15:00:00Z"', once)
        self.assertTrue(once.endswith('\n\n文章\n'))
        later = module.stamp_publication(once, datetime(2026, 10, 22, 16, 0, tzinfo=timezone.utc))
        self.assertEqual(later.count('lastPublishedAt:'), 1)
        self.assertIn('2026-10-22T16:00:00Z', later)

    def test_refuses_content_without_frontmatter(self):
        with self.assertRaises(ValueError):
            module.stamp_publication('just text', datetime.now(timezone.utc))


if __name__ == '__main__':
    unittest.main()
