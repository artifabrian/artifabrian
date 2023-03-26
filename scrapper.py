import datetime
import jinja2
import requests
import trio
from bs4 import BeautifulSoup

URL = 'https://www.joaoleal.com/'
BLOG_URL = URL + 'blog'


def fetch_blog_posts(url: str) -> requests.Response:
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch page with status code {response.status_code}")
    return response


def parse_blog_posts(html: str) -> list:
    soup = BeautifulSoup(html, 'html.parser')
    blog_posts = soup.find_all('div', class_='block-blog-list-item')
    return blog_posts


def extract_post_data(post) -> dict:
    post_url = URL + post.find('a', class_='block-blog-list-item__content')['href']
    post_title = post.find('h3', class_='font-primary block-blog-list-item__title').text.strip()
    post_date = datetime.datetime.strptime(
        post.find('p', class_='blog-list-item-meta__subtitle').find('span').text.strip(), '%m/%d/%Y')
    return {
        "post_url": post_url,
        "post_date": post_date,
        "post_title": post_title
    }


def get_latest_blog_posts() -> dict:
    response = fetch_blog_posts(BLOG_URL)
    blog_posts = parse_blog_posts(response.text)

    post_data = {
        "post_url_1": "",
        "post_title_1": "",
        "post_date_1": datetime.date.today(),
        "post_url_2": "",
        "post_title_2": "",
        "post_date_2": datetime.date.today(),
    }

    if len(blog_posts) >= 2:
        post_1 = extract_post_data(blog_posts[0])
        post_data["post_url_1"] = post_1["post_url"]
        post_data["post_title_1"] = post_1["post_title"]
        post_data["post_date_1"] = post_1["post_date"]

        post_2 = extract_post_data(blog_posts[1])
        post_data["post_url_2"] = post_2["post_url"]
        post_data["post_title_2"] = post_2["post_title"]
        post_data["post_date_2"] = post_2["post_date"]

    return post_data


def generate_readme(
        username: str,
        post_url_1: str,
        post_title_1: str,
        post_date_1: datetime.datetime,
        post_url_2: str,
        post_title_2: str,
        post_date_2: datetime.datetime,
):
    with open("TEMPLATE.md", "r", encoding="utf-8") as file:
        template = jinja2.Template(file.read())

    today = datetime.date.today()

    return template.render(
        post_url_1=post_url_1,
        post_title_1=post_title_1,
        post_date_1=post_date_1.date().isoformat(),
        post_url_2=post_url_2,
        post_title_2=post_title_2,
        post_date_2=post_date_2.date().isoformat(),
        username=username,
        today=today.isoformat(),
    )


async def main(
        username: str,
):
    latest_blog_posts = get_latest_blog_posts()

    print(generate_readme(username,
                          latest_blog_posts['post_url_1'],
                          latest_blog_posts['post_title_1'],
                          latest_blog_posts['post_date_1'],
                          latest_blog_posts['post_url_2'],
                          latest_blog_posts['post_title_2'],
                          latest_blog_posts['post_date_2'],
                          ))


if __name__ == "__main__":
    import fire


    def cli(
            username: str,
    ):
        """Provide a CLI for the script for use by Fire."""
        trio.run(main, username)


    fire.Fire(cli)
