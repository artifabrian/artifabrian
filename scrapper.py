import datetime

import jinja2
import requests
import trio
from bs4 import BeautifulSoup

url = 'https://www.joaoleal.com/'


def get_latest_blog_posts(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch page with status code {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    blog_posts = soup.find_all('div', class_='block-blog-list-item')

    post_url_1 = ""
    post_title_1 = ""
    post_date_1 = datetime.date.today()
    post_url_2 = ""
    post_title_2 = ""
    post_date_2 = datetime.date.today()

    if len(blog_posts) >= 2:
        post_1 = blog_posts[0]
        post_url_1 = post_1.find('a', class_='block-blog-list-item__content')['href']
        post_title_1 = post_1.find('h3', class_='font-primary block-blog-list-item__title').text.strip()
        post_date_1 = datetime.datetime.strptime(
            post_1.find('p', class_='blog-list-item-meta__subtitle').find('span').text.strip(), '%m/%d/%Y')

        post_2 = blog_posts[1]
        post_url_2 = post_2.find('a', class_='block-blog-list-item__content')['href']
        post_title_2 = post_2.find('h3', class_='font-primary block-blog-list-item__title').text.strip()
        post_date_2 = datetime.datetime.strptime(
            post_2.find('p', class_='blog-list-item-meta__subtitle').find('span').text.strip(), '%m/%d/%Y')

    return {
        "post_url_1": post_url_1,
        "post_date_1": post_date_1,
        "post_title_1": post_title_1,
        "post_url_2": post_url_2,
        "post_date_2": post_date_2,
        "post_title_2": post_title_2
    }


def generate_readme(

        username: str,
        post_url_1: str,
        post_title_1: str,
        post_date_1: datetime.datetime,
        post_url_2: str,
        post_title_2: str,
        post_date_2: datetime.datetime,
):
    """Create the README from TEMPLATE.md."""
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


latest_blog_posts = get_latest_blog_posts(url + '/blog')
print(latest_blog_posts)


async def main(
        username: str,
):
    latest_blog_posts = get_latest_blog_posts(url + '/blog')

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
        trio.run(main,  username)


    fire.Fire(cli)
