# coding=utf-8
#
# 封装 flask_sqlalchemy, 可自己指定 bind_key 实现读写分离
# 支持 __bind_key__ 以及 get_session(bind_key='key')
#
# 若 TableModel中定义了__bind_key__，但get_session中又指定了bind_key，则get_session优先级高于定义的 __bind_key__
#

from flask_sqlalchemy import (
    SignallingSession, SQLAlchemy,
    get_state,
    BaseQuery, Model)
from sqlalchemy import orm
from sqlalchemy.orm import Session as SessionBase


class RoutingSession(SignallingSession):
    def __init__(self, db, autocommit=False, autoflush=True, **options):
        self.bind_key = None
        if 'bind_key' in options:
            self.bind_key = options.pop('bind_key')

        super(RoutingSession, self).__init__(db,
                                             autocommit=autocommit,
                                             autoflush=autoflush,
                                             **options)

    def get_bind(self, mapper=None, clause=None):
        """Return the engine or connection for a given model or
                table, using the ``__bind_key__`` if it is set.
                """
        # mapper is None if someone tries to just get a connection
        if mapper is not None:
            try:
                # SA >= 1.3
                persist_selectable = mapper.persist_selectable
            except AttributeError:
                # SA < 1.3
                persist_selectable = mapper.mapped_table

            info = getattr(persist_selectable, 'info', {})
            bind_key = self.bind_key if self.bind_key else info.get('bind_key')
            if bind_key is not None:
                state = get_state(self.app)
                return state.db.get_engine(self.app, bind=bind_key)
        return SessionBase.get_bind(self, mapper, clause)


class RoutingSQLAlchemy(SQLAlchemy):
    """
    Example:
        db = RoutingSQLAlchemy(session_options={
            'autocommit': True
        })

        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://master_uri'
        app.config['SQLALCHEMY_POOL_SIZE'] = 10
        app.config['SQLALCHEMY_BINDS'] = {
            'master': 'postgresql://master_uri',
            'slave': 'postgresql://slave_uri',
            'other_db': 'mysql://other_uri'
        }
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)


        ### use slave connection  ###
        se = db.get_session(bind_key='slave')
        se.query(TableModel).all()

        ### use master connection  ###
        TableModel.query.all()
        db.session.query(TableModel).all()

        se = db.get_session(bind_key='master')
        with se.begin():
            se.add(TableModel())
    """
    def __init__(self, app=None, use_native_unicode=True, session_options=None,
                 metadata=None, query_class=BaseQuery, model_class=Model,
                 engine_options=None):
        super(RoutingSQLAlchemy, self).__init__(app=app, use_native_unicode=use_native_unicode,
                                                session_options=session_options,
                                                metadata=metadata, query_class=query_class,
                                                model_class=model_class,
                                                engine_options=engine_options)

        self.global_session_options = session_options
        if self.global_session_options is None:
            self.global_session_options = {}

    def create_session(self, options):
        return orm.sessionmaker(class_=RoutingSession, db=self, **options)

    def get_session(self, bind_key=None):
        options = self.global_session_options
        if bind_key is not None:
            options['bind_key'] = bind_key

        return self.create_scoped_session(options)

