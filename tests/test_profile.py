import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from generate_profile import parse_article_frontmatter, streaks

class TestProfile(unittest.TestCase):
    def test_all_svgs_are_valid(self):
        for name in ('hero','tech-stack','project-hana','project-portfolio','project-fpt','stats','contributions'):
            path = ROOT/'assets'/f'{name}.svg'
            self.assertTrue(path.exists(), str(path))
            root = ET.parse(path).getroot()
            self.assertTrue(root.tag.endswith('svg'))
            self.assertEqual(root.attrib.get('viewBox') is not None, True)

    def test_readme_paths_and_markers(self):
        readme = (ROOT/'README.md').read_text(encoding='utf8')
        self.assertIn('<!-- ARTICLES:START -->', readme)
        self.assertIn('<!-- ARTICLES:END -->', readme)
        for name in ('hero','tech-stack','project-hana','project-portfolio','project-fpt','stats','contributions'):
            self.assertIn(f'./assets/{name}.svg', readme)

    def test_streak_today_and_yesterday(self):
        today = date(2026,10,23)
        ds = [{'date':(today-timedelta(days=i)).isoformat(), 'contributionCount': c}
              for i,c in enumerate([0,2,3,0,1,2,1])]
        self.assertEqual(streaks(ds,today),(2,3))
        ds[0]['contributionCount']=1
        self.assertEqual(streaks(ds,today),(3,3))

    def test_article_frontmatter(self):
        article = parse_article_frontmatter('---\ntitle: My Note\ndate: 2026-05-12\n---\nhi',
                                             'src/content/blog/my-note.mdx')
        self.assertEqual(article['url'],'https://nguyendao16.github.io/blog/my-note/')
        self.assertEqual(article['date'],'2026-05-12')
        self.assertIsNone(parse_article_frontmatter('---\ntitle: Draft\ndate: 2026-05-12\ndraft: true\n---\n',
                                                      'src/content/blog/draft.md'))

if __name__ == '__main__':
    unittest.main()
