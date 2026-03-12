from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import LandingPageView, JoinRequestView, JoinRequestListView, process_join_request, DashboardView, UserProfileView, UserPasswordChangeView, login_success, SupplierListView, CreateSupplierView, SupplierUpdateView, SupplierDeleteView, BuyerListView, CreateBuyerView, BuyerUpdateView, BuyerDeleteView, WorkerListView, CreateWorkerView, WorkerDeleteView, ManagerListView, ManagerCreateView, ManagerDeleteView, TransactionListView, RecordSupplyView, RecordSaleView, SiteListView, SiteDetailView, SaveMilkRecordView, ChatView, NotificationListView, TrainingView, TrainingResourceCreateView, TrainingResourceDeleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('login-success/', login_success, name='login_success'),
    path('', LandingPageView.as_view(), name='home'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/password/', UserPasswordChangeView.as_view(), name='password_change'),
    path('request-join/', JoinRequestView.as_view(), name='join_request'),
    path('reports/supplier/<int:pk>/', supplier_report, name='supplier_report'),
    path('reports/buyer/<int:pk>/', buyer_report, name='buyer_report'),
    path('join-requests/', JoinRequestListView.as_view(), name='join_request_list'),
    path('join-requests/<int:pk>/<str:action>/', process_join_request, name='process_join_request'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('training/', TrainingView.as_view(), name='training'),
    path('training/add/', TrainingResourceCreateView.as_view(), name='training_add'),
    path('training/<int:pk>/delete/', TrainingResourceDeleteView.as_view(), name='training_delete'),
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', CreateSupplierView.as_view(), name='supplier_add'),
    path('suppliers/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),
    path('buyers/', BuyerListView.as_view(), name='buyer_list'),
    path('buyers/add/', CreateBuyerView.as_view(), name='buyer_add'),
    path('buyers/<int:pk>/edit/', BuyerUpdateView.as_view(), name='buyer_edit'),
    path('buyers/<int:pk>/delete/', BuyerDeleteView.as_view(), name='buyer_delete'),
    path('workers/', WorkerListView.as_view(), name='worker_list'),
    path('workers/add/', CreateWorkerView.as_view(), name='worker_add'),
    path('workers/<int:pk>/delete/', WorkerDeleteView.as_view(), name='worker_delete'),
    path('workers/<int:pk>/pay/', pay_worker, name='worker_pay'),
    path('managers/', ManagerListView.as_view(), name='manager_list'),
    path('managers/add/', ManagerCreateView.as_view(), name='manager_add'),
    path('managers/<int:pk>/delete/', ManagerDeleteView.as_view(), name='manager_delete'),
    path('sites/', SiteListView.as_view(), name='site_list'),
    path('sites/<int:pk>/', SiteDetailView.as_view(), name='site_detail'),
    path('api/save-milk/', SaveMilkRecordView.as_view(), name='save_milk_record'),
    path('expenses/add/', ExpenseCreateView.as_view(), name='expense_add'),
    path('losses/add/', MilkLossCreateView.as_view(), name='loss_add'),
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions/supply/new/', RecordSupplyView.as_view(), name='record_supply'),
    path('transactions/sales/new/', RecordSaleView.as_view(), name='record_sale'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('users.urls')),
    path('api/business/', include('business.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/communication/', include('communication.urls')),
    path('api/training/', include('training.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
