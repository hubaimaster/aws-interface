# """
# Track how long the user or guest stays on the page and what actions they take
# """
# from dashboard.models import Event, Tracker
#
#
# class Tracking(object):
#     request = None
#     session = None
#     tracker = None
#
#     def __init__(self, request):
#         self.request = request
#         self._enroll_session(request)
#         funnel = request.META.get('HTTP_REFERER', None)
#         self._put_tracker(funnel)
#
#     def _enroll_session(self, request):
#         self.session = request.session
#
#     def _put_tracker(self, funnel=None):
#         if 'tracker_id' in self.session:
#             tracker_id = self.session['tracker_id']
#             tracker = Tracker.objects.get(id=tracker_id)
#         else:
#             tracker = Tracker()
#         tracker.funnel = funnel
#         if self.request.user.is_authenticated:
#             tracker.user = self.request.user
#         tracker.save()
#         self.tracker = tracker
#         self.session['tracker_id'] = tracker.id
#
#     def _put_event(self, action, amount, description, target, event_id=None):
#         if event_id:
#             event = Event.objects.get(id=event_id)
#         else:
#             event = Event()
#         event.action = action
#         event.amount = amount
#         event.description = description
#         event.target = target
#         if self.request.user.is_authenticated:
#             event.user = self.request.user
#         event.tracker = self.tracker
#         event.save()
#
#     def view_url(self, url):
#         self._put_event('view_url', 0, 'View {}'.format(url), url)
#
#     def click_button(self, button_name):
#         self._put_event('click_button', 0, 'Click {}'.format(button_name), button_name)

#       Do not use this code
