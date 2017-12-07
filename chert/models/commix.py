import datetime
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy import Date, Time
from sqlalchemy import Enum
from sqlalchemy import PickleType
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ..alchemy import TimeStampMixin

# ########################## RULES ##############################
# A User has a single Contact (one contact:many users).
#
#   An Event depends on an EventType.  An EventType must be
# created before an Event is created.
#
# A "host" must have a Venue to promote an Event.
#
# //Multiple "hosts" can promote Event(s) at the same Venue
#
# //An Event can have multiple Venues (such as a festival)
#
# //When a "host" claims a Venue, this host selects the other
# //hosts that can promote Event(s) at this Venue.
#
# The three commented options above are too time consuming
# to implement at this point, while also needing some
# coordination and design considerations outside the scope
# of the website.
#
# I have just decided to layout the basic data model for
# festivals.  A festival is a collection of events that
# will span for a length of time (a day, a weekend, a week
# or two).  This will allow user to host a festival and
# invite other users to host events.
#
#
################################################################


RoleType = Enum('admin', 'host', 'user', 'guest', name='roletype')


class AddressMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'addresses'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def street(self):
        return Column(Unicode(150))

    @declared_attr
    def street2(self):
        return Column(Unicode(150))

    @declared_attr
    def city(self):
        return Column(Unicode(50))

    @declared_attr
    def state(self):
        return Column(Unicode(2))

    @declared_attr
    def zip(self):
        return Column(Unicode(10))


class ContactMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'addresses'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def firstname(self):
        return Column(Unicode(50))

    @declared_attr
    def lastname(self):
        return Column(Unicode(50))

    @declared_attr
    def email(self):
        return Column(Unicode(150))

    @declared_attr
    def phone(self):
        return Column(Unicode(20))

    @declared_attr
    def users(self):
        return relationship('User')


class AudienceMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'audiences'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def location(self):
        return Column(Unicode(50))

    def __init__(self, location=None):
        self.location = location


class VenueMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'venues'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def name(self):
        return Column(Unicode(50))

    @declared_attr
    def audience_id(self):
        return Column(Integer, ForeignKey('audiences.id'))

    @declared_attr
    def address_id(self):
        return Column(Integer, ForeignKey('addresses.id'))

    @declared_attr
    def user_id(self):
        return Column(Integer, ForeignKey('users.id'))

    @declared_attr
    def description(self):
        return Column(UnicodeText)

    def __init__(self, user_id, name=None, audience_id=None):
        self.user_id = user_id
        self.name = name
        self.audience_id = audience_id


class EventTypeMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'event_types'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def name(self):
        return Column(Unicode(50), unique=True)

    def __init__(self, name=None):
        self.name = name


# FIXME
class EventTypeColorMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'event_type_colors'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def color(self):
        return Column(Unicode(50))

    def __init__(self, color):
        self.color = color


class EventMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'events'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def start_date(self):
        return Column(Date)

    @declared_attr
    def start_time(self):
        return Column(Time)

    # FIXME should I use hybrid attribute?
    @declared_attr
    def starts_at(self):
        return datetime.datetime.combine(self.start_date, self.start_time)

    @declared_attr
    def end_date(self):
        return Column(Date)

    @declared_attr
    def end_time(self):
        return Column(Time)

    # FIXME should I use hybrid attribute?
    @declared_attr
    def ends_at(self):
        return datetime.datetime.combine(self.end_date, self.end_time)

    @declared_attr
    def all_day(self):
        return Column(Boolean('all_day_event'), default=False)

    @declared_attr
    def title(self):
        return Column(Unicode(255))

    @declared_attr
    def description(self):
        return Column(UnicodeText)

    @declared_attr
    def originator(self):
        return Column(Integer, ForeignKey('users.id'))

    @declared_attr
    def event_type(self):
        return Column(Integer, ForeignKey('event_types.id'))

    @declared_attr
    def venue_id(self):
        return Column(Integer, ForeignKey('venues.id'))

    @declared_attr
    def venue(self):
        return relationship('Venue', secondary='event_venues',
                            backref='events')

    def __init__(self, originator):
        self.originator = originator


class EventVenueMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'event_venues'

    @declared_attr
    def event_id(self):
        return Column(Integer, ForeignKey('events.id'), primary_key=True)

    @declared_attr
    def venue_id(self):
        return Column(Integer, ForeignKey('venues.id'), primary_key=True)

    def __init__(self, event_id, venue_id):
        self.event_id = event_id
        self.venue_id = venue_id


class VenueInfoMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'venue_info'

    @declared_attr
    def id(self):
        return Column(Integer, ForeignKey('venues.id'), primary_key=True)

    @declared_attr
    def info(self):
        return Column(PickleType)

    def __init__(self, id, info):
        self.id = id
        self.info = info


class FestivalMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'festivals'

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True)


class FestivalEventMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'festival_events'

    @declared_attr
    def festival_id(self):
        return Column(Integer, ForeignKey('festival.id'), primary_key=True)

    @declared_attr
    def event_id(self):
        return Column(Integer, ForeignKey('events.id'), primary_key=True)


class UserInfoMixin(TimeStampMixin):
    @declared_attr
    def __tablename__(self):
        return 'commix_user_info'

    @declared_attr
    def id(self):
        return Column(Integer, ForeignKey('users.id'), primary_key=True)

    @declared_attr
    def contact_id(self):
        return Column(Integer, ForeignKey('contacts.id'))

    @declared_attr
    def role(self):
        return Column(RoleType)

    @declared_attr
    def default_audience_id(self):
        return Column(Integer, ForeignKey('audiences.id'))

    @declared_attr
    def contact(self):
        return relationship('Contact')
