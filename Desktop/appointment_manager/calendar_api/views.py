from django.http import JsonResponse
from rest_framework.views import APIView
from django.views import View
from django.shortcuts import redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from django.contrib import messages
import os
import json
from django.shortcuts import render
from rest_framework.response import Response
import datetime
from accounts.models import *
from manager.models import *
from accounts.decorators import *
# Set to True to enable OAuthlib's HTTPs verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class GoogleCalendarInitView(View):
    """
    Initiate the OAuth2 authorization flow.
    """

    def get(self, request, *args, **kwargs):
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.events']
        )
        flow.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect'

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
        )

        # Store the state so the callback can verify the auth server response.
        request.session['state'] = state
        # Redirect the user to the authorization URL.
        return redirect(authorization_url)


class GoogleCalendarRedirectView(View):
    """
    Callback view to handle the response from Google OAuth2 authorization server.

    This view is registered as the redirect_uri in the Google OAuth2 client
    configuration. The authorization server will redirect the user to this view
    after the user has granted or denied permission to the client.
    """

    def get(self, request, *args, **kwargs):
        # Specify the state when creating the flow in the callback so that it can
        # verified in the authorization server response.
        state = request.GET.get('state')
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.events'],
            state=state
        )
        flow.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect'

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        # Store the credentials in the session.
        credentials = flow.credentials

        request.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        # Fetching of events is done in a separate view.
        # Here we just redirect to the events view.
        return redirect('event_manager')


class GoogleCalendarEventsView(View):
    """
    Fetch events from Google Calendar.
    """

    def get(self, request, *args, **kwargs):
        print(request.user)
        credentials = Credentials(
            **request.session['credentials']
        )
        doctors=Doctor.objects.all()
        doc=[]
        for doctor in doctors:
            if not hasattr(doctor,'schedule'):
                doc.append(doctor.id)        
        doctors=Doctor.objects.all().exclude(id__in=doc)
        return render(request,'manager/book_appointment.html',{'doctors':doctors})
    
    def post(self,request,*args,**kwargs):
        credentials = Credentials(
            **request.session['credentials']
        )
        service = build('calendar', 'v3', credentials=credentials)
        dt=datetime.datetime.strptime(request.POST.get('booking_date'),"%Y-%m-%d").date()
        doctor=Doctor.objects.get(id=request.POST.get('doctor'))
        slot=AvailableSlots.objects.get(id=request.POST.get('slot'))
        a=str(slot.start)
        b=str(slot.end)
        s=datetime.datetime.strptime(str(dt)+'T'+a,'%Y-%m-%dT%H:%M:%S')
        e=datetime.datetime.strptime(str(dt)+'T'+b,'%Y-%m-%dT%H:%M:%S')
        event={
            'summary': f"{request.user.first_name} {request.user.last_name}'s appointment with Dr. {doctor.user.first_name}",
            'location': request.POST.get('location'),
            'description':request.POST.get('description'),
            'start': {
                'dateTime':str(s.isoformat('T')),
                'timeZone': "Asia/Kolkata"
            },
            'end': {
                'dateTime': str(e.isoformat('T')),
                'timeZone': "Asia/Kolkata"
            },
        }
        events_result=service.events().insert(calendarId="primary",body=event).execute()
        print(f"Event Created: {events_result.get('htmlLink')}")
        booking.objects.create(
            patient=Patient.objects.get(user_id=request.user.id),
            doctor=doctor,
            booking_date=dt,
            start=slot.start,
            end=slot.end,
            eventid=events_result.get('id')
        )
        slot.delete()
        return redirect('user_home')

