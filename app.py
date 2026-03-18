from flask import Flask, render_template_string, request, redirect, url_for
import requests

app = Flask(__name__)

# HTML template for posts dashboard
POSTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Posts | Editorial</title>
    <!-- Premium Typography -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #fdfdfd;
            --text-main: #1a1a1a;
            --text-muted: #666666;
            --accent-color: #0056b3;
            --border-color: #eeeeee;
            --card-bg: #ffffff;
            --font-serif: 'Playfair Display', serif;
            --font-sans: 'Inter', sans-serif;
            --max-width: 800px;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--font-sans);
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            padding: 60px 20px;
        }

        .container {
            max-width: var(--max-width);
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 80px;
        }

        h1 {
            font-family: var(--font-serif);
            font-size: 3.5rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin-bottom: 10px;
            color: var(--text-main);
        }

        .subtitle {
            font-size: 1.1rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 500;
        }

        .posts-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 60px;
        }

        .post-card {
            background: var(--card-bg);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 40px;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            text-decoration: none;
            color: inherit;
            display: block;
            opacity: 0;
            animation: fadeInUp 0.8s ease forwards;
        }

        .post-card:hover {
            opacity: 0.9;
            transform: translateY(-4px);
        }

        .post-img-container {
            width: 100%;
            height: 450px;
            overflow: hidden;
            border-radius: 4px;
            margin-bottom: 25px;
            background-color: #f0f0f0;
        }

        .post-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.8s cubic-bezier(0.165, 0.84, 0.44, 1);
        }

        .post-card:hover .post-img {
            transform: scale(1.05);
        }

        .post-meta {
            font-size: 0.85rem;
            color: var(--accent-color);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
        }

        .post-title {
            font-family: var(--font-serif);
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.2;
            color: var(--text-main);
            margin-bottom: 15px;
        }

        .post-excerpt {
            font-size: 1.1rem;
            color: var(--text-muted);
            margin-bottom: 20px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .read-more {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .read-more::after {
            content: '→';
            transition: transform 0.3s ease;
        }

        .post-card:hover .read-more::after {
            transform: translateX(5px);
        }

        .error {
            background-color: #fff5f5;
            color: #c53030;
            padding: 20px;
            border-radius: 4px;
            border: 1px solid #feb2b2;
            text-align: center;
        }

        @media (max-width: 600px) {
            h1 { font-size: 2.5rem; }
            .post-title { font-size: 1.8rem; }
            .post-img-container { height: 300px; }
            body { padding: 40px 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="subtitle">The Daily Journal</div>
            <h1>Editorial Postings</h1>
        </header>

        <main class="posts-grid">
            {% if posts %}
                {% for post in posts %}
                    <a href="{{ url_for('post_detail', post_id=post.id) }}" class="post-card" style="animation-delay: {{ loop.index0 * 0.1 if loop.index0 < 20 else 2 }}s">
                        <div class="post-img-container">
                            <img class="post-img" src="https://picsum.photos/900/600?random={{ post.id }}" alt="{{ post.title }}" loading="lazy">
                        </div>
                        <div class="post-meta">Story ID: {{ post.id }} • Author {{ post.userId }}</div>
                        <h2 class="post-title">{{ post.title }}</h2>
                        <p class="post-excerpt">{{ post.body }}</p>
                        <div class="read-more">Read Full Story</div>
                    </a>
                {% endfor %}
            {% else %}
                <div class="error">
                    <strong>Unable to load stories.</strong>
                </div>
            {% endif %}
        </main>
    </div>
</body>
</html>
"""

# HTML template for post detail
DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article Detail | Editorial</title>
    <!-- Premium Typography -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #fdfdfd;
            --text-main: #1a1a1a;
            --text-muted: #666666;
            --accent-color: #0056b3;
            --border-color: #eeeeee;
            --card-bg: #ffffff;
            --font-serif: 'Playfair Display', serif;
            --font-sans: 'Inter', sans-serif;
            --max-width: 740px;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: var(--font-sans);
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.8;
            padding: 60px 20px;
        }
        
        .container {
            max-width: var(--max-width);
            margin: 0 auto;
            animation: fadeInUp 0.8s ease-out forwards;
        }
        
        .back-link {
            display: inline-flex;
            align-items: center;
            color: var(--text-muted);
            text-decoration: none;
            margin-bottom: 50px;
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            transition: color 0.3s ease;
        }
        
        .back-link:hover {
            color: var(--text-main);
        }

        .back-link::before {
            content: '←';
            margin-right: 8px;
        }
        
        .post-header {
            margin-bottom: 50px;
        }
        
        .post-meta {
            font-size: 0.9rem;
            color: var(--accent-color);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 15px;
        }
        
        .post-title {
            font-family: var(--font-serif);
            font-size: 3.2rem;
            font-weight: 800;
            color: var(--text-main);
            line-height: 1.1;
            margin-bottom: 25px;
            letter-spacing: -0.02em;
        }

        .post-author-box {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1rem;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            padding: 15px 0;
            margin-bottom: 40px;
        }

        .author-name {
            color: var(--text-main);
            font-weight: 600;
        }
        
        .post-image-container {
            margin: 40px 0;
        }
        
        .post-image-container img {
            width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }
        
        .post-body {
            font-size: 1.25rem;
            color: #333;
            margin-top: 40px;
            white-space: pre-line;
            font-family: serif;
            line-height: 1.9;
        }

        /* Comments Section Styling */
        .comments-header {
            margin-top: 80px;
            margin-bottom: 40px;
            border-top: 2px solid var(--text-main);
            padding-top: 40px;
        }

        .comments-title {
            font-family: var(--font-serif);
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-main);
        }

        .comment {
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 1px solid var(--border-color);
            opacity: 0;
            animation: fadeInUp 0.6s ease forwards;
        }

        .comment:last-child {
            border-bottom: none;
        }

        .comment-header {
            margin-bottom: 10px;
        }

        .comment-author {
            font-weight: 700;
            color: var(--text-main);
            font-size: 1rem;
        }

        .comment-email {
            font-size: 0.85rem;
            color: var(--accent-color);
            font-weight: 500;
        }

        .comment-body {
            font-size: 1.05rem;
            color: #444;
            line-height: 1.6;
        }
        
        .error {
            background-color: #fff5f5;
            color: #c53030;
            border-radius: 4px;
            border: 1px solid #feb2b2;
            padding: 30px;
            text-align: center;
        }

        @media (max-width: 600px) {
            .post-title { font-size: 2.2rem; }
            body { padding: 40px 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <a href="{{ url_for('index') }}" class="back-link">Back to Journal</a>
        </nav>
        
        {% if post %}
            <article>
                <header class="post-header">
                    <div class="post-meta">Story ID: {{ post.id }} • Archive</div>
                    <h1 class="post-title">{{ post.title }}</h1>
                    <div class="post-author-box">
                        By <span class="author-name">{{ user.name }}</span> • @{{ user.username }}
                    </div>
                </header>
                
                <div class="post-image-container">
                    <img src="https://picsum.photos/1200/800?random={{ post.id }}" alt="{{ post.title }}">
                </div>
                
                <div class="post-body">
                    {{ post.body }}
                </div>
            </article>

            <section>
                <div class="comments-header">
                    <h2 class="comments-title">Discussion ({{ comments|length }})</h2>
                </div>
                <div>
                    {% for comment in comments %}
                        <div class="comment" style="animation-delay: {{ 0.5 + (loop.index0 * 0.1) if loop.index0 < 10 else 1.5 }}s">
                            <div class="comment-header">
                                <div class="comment-author">{{ comment.name }}</div>
                                <div class="comment-email">{{ comment.email }}</div>
                            </div>
                            <div class="comment-body">{{ comment.body }}</div>
                        </div>
                    {% endfor %}
                </div>
            </section>
        {% else %}
            <div class="error">
                <strong>Something went wrong.</strong>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Fetch and display all posts"""
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts')
        posts = response.json()[:20]
        return render_template_string(POSTS_TEMPLATE, posts=posts)
    except Exception as e:
        return render_template_string(POSTS_TEMPLATE, posts=None)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    """Fetch and display a single post with user details and comments"""
    try:
        # Fetch post details
        post_response = requests.get(f'https://jsonplaceholder.typicode.com/posts/{post_id}')
        post = post_response.json()
        
        # Fetch user info using userId from post
        user_id = post.get('userId')
        user_response = requests.get(f'https://jsonplaceholder.typicode.com/users/{user_id}')
        user = user_response.json()

        # Fetch comments
        comments_response = requests.get(f'https://jsonplaceholder.typicode.com/posts/{post_id}/comments')
        comments = comments_response.json()
        
        return render_template_string(DETAIL_TEMPLATE, post=post, user=user, comments=comments)
    except Exception as e:
        return render_template_string(DETAIL_TEMPLATE, post=None, user=None, comments=[])

if __name__ == '__main__':
    app.run(debug=True, port=5000)

