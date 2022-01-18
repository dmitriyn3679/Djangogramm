sql_follows = '''
    SELECT to_user_id
    FROM web_follows
    WHERE from_user_id = {};
'''

sql_posts = '''
    --Post:id text pub_date username avatar likes comments_count
    SELECT p.id, p.text, p.pub_date, u.username, u.avatar,
        (
            SELECT count(id)
            FROM web_post_like_user plu
            WHERE plu.post_id = p.id
        ) likes,
        (
            SELECT count(id)
            FROM web_comment c
            WHERE c.post_id = p.id
        ) comments_count
    FROM web_post p
    JOIN web_user u ON u.id = p.user_id
    WHERE user_id IN ({})
    ORDER BY p.pub_date DESC, p.id DESC;
'''

sql_media = '''
    --Media:id media post_id
    SELECT id, media, post_id
    FROM web_media
    WHERE post_id IN ({});
'''

sql_comments = '''
    --Comment:id text post_id username
    SELECT c.id, c.text, c.post_id, u.username
    FROM web_comment c
    JOIN web_user u ON u.id = c.user_id
    WHERE c.post_id IN ({});
'''