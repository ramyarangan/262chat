from app import db


class Seen(db.Model):
    '''
    last seen message id, per user per group
    '''

    __tablename__ = 'seen'

    id = db.Column(db.Integer, primary_key=True)

    viewer = db.Column(db.String(20), db.ForeignKey('user.username'))
    room_user = db.Column(db.String(20), db.ForeignKey('user.username'), 
        nullable=True)
    room_group = db.Column(db.String(20), db.ForeignKey('group.groupname'),
        nullable=True)
    last_seen_id = db.Column(db.Integer, db.ForeignKey('message.id'), default=0)


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text(), nullable=False)
    timestamp = db.Column(db.DateTime)

    sender_username = db.Column(db.String(20), db.ForeignKey('user.username'), \
        nullable=False)
    to_username = db.Column(db.String(20), db.ForeignKey('user.username'), \
        nullable=True)
    to_groupname = db.Column(db.String(40), db.ForeignKey('group.groupname'), \
        nullable=True)

    def __repr__(self):
        return '<Message %r>' % (self.body)

users_groups_assoc_table = db.Table('usersgroups', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'),)
)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True)

    received_msgs = db.relationship('Message', backref='to_user', lazy='dynamic', \
        foreign_keys=[Message.to_username])
    sent_msgs = db.relationship('Message', lazy='dynamic', \
        foreign_keys=[Message.sender_username])

    groups = db.relationship("Group", \
        secondary=users_groups_assoc_table, \
        back_populates="users")

    def __repr__(self):
        return '<User %r>' % (self.username)

class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(40), index=True, unique=True)
    
    msgs = db.relationship('Message', backref='to_group', lazy='dynamic', foreign_keys=[Message.to_groupname])
    
    users = db.relationship("User", secondary=users_groups_assoc_table, \
        back_populates="groups")

    def __repr__(self):
        return '<Group %r>' % (self.groupname)



