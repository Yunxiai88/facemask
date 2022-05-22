from application import db, create_app, models
from werkzeug.security import generate_password_hash

app=create_app()

with app.app_context():
    db.create_all()

    if not models.User.query.filter_by(email = 'admin').first():
        user = models.User(name='admin', email='admin@gmail.com')
        user.set_password("admin")
        user.roles.append(models.Role(name='admin'))
        user.roles.append(models.Role(name='user'))

        db.session.add(user)
        db.session.commit()