from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    u = User.query.filter_by(username='test_user_for_comp').first()
    if not u:
        u = User(username='test_user_for_comp', password=generate_password_hash('testpass'))
        db.session.add(u)
        db.session.commit()
        print('Created test user')
    else:
        print('Test user exists')

client = app.test_client()
rv = client.post('/login', data={'username':'test_user_for_comp','password':'testpass'}, follow_redirects=True)
print('Login status code:', rv.status_code)
rv2 = client.get('/compendio')
print('GET /compendio status code:', rv2.status_code)
print('Response length:', len(rv2.data))
print(rv2.data.decode('utf-8')[:800])
