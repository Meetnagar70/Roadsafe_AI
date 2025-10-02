from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_page, name='dashboard'),
    
    # URL for the link in the navbar. It has no parameters.
    path('district-analysis/', views.district_page, name='district_analysis_form'),

    # URL for the links from the state page. It has parameters.
    path('state/<str:state_name>/district/<str:district_name>/', views.district_page, name='district_detail'),

    # This URL is still needed for the State dropdown in the navbar
    path('state/<str:state_name>/', views.state_page, name='state_detail'),

    path('submit/', views.submit_page, name='submit_page'),
     path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]