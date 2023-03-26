import datetime
from dataclasses import dataclass
from typing import List

import jinja2
import requests
from bs4 import BeautifulSoup
import trio
import fire

URL = "https://www.joaoleal.com/"
BLOG_URL = URL + "blog"


@dataclass
class BlogPost:
    post_url: str
    post_title: str
    post_date: datetime.datetime


class BlogScraper:
    def fetch_blog_posts(self, url: str) -> requests.Response:
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch page with status code {response.status_code}")
        return response

    def parse_blog_posts(self, html: str) -> List[BeautifulSoup]:
        soup = BeautifulSoup(html, "html.parser")
        return soup.find_all("div", class_="block-blog-list-item")

    def extract_post_data(self, post: BeautifulSoup) -> BlogPost:
        post_url = URL + post.find("a", class_="block-blog-list-item__content")["href"]
        post_title = post.find("h3", class_="font-primary block-blog-list-item__title").text.strip()
        post_date = datetime.datetime.strptime(
            post.find("p", class_="blog-list-item-meta__subtitle").find("span").text.strip(), "%m/%d/%Y")
        return BlogPost(post_url, post_title, post_date)

    def get_latest_blog_posts(self) -> List[BlogPost]:
        response = self.fetch_blog_posts(BLOG_URL)
        blog_posts = self.parse_blog_posts(response.text)
        return [self.extract_post_data(post) for post in blog_posts[:2]]


class ReadmeGenerator:
    @staticmethod
    def render_template(username: str, posts: List[BlogPost]) -> str:
        with open("TEMPLATE.md", "r", encoding="utf-8") as file:
            template = jinja2.Template(file.read())

        today = datetime.date.today()

        return template.render(
            post_url_1=posts[0].post_url,
            post_title_1=posts[0].post_title,
            post_date_1=posts[0].post_date.date().isoformat(),
            post_url_2=posts[1].post_url,
            post_title_2=posts[1].post_title,
            post_date_2=posts[1].post_date.date().isoformat(),
            username=username,
            today=today.isoformat(),
        )


async def main(username: str):
    scraper = BlogScraper()
    latest_blog_posts = scraper.get_latest_blog_posts()
    readme = ReadmeGenerator.render_template(username, latest_blog_posts)
    print(readme)


if __name__ == "__main__":
    def cli(username: str):
        """Provide a CLI for the script for use by Fire."""
        trio.run(main, username)


    fire.Fire(cli)
