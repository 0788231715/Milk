from django.views.generic import TemplateView, ListView, CreateView, DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import timedelta
import calendar
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from business.models import Supplier, Buyer, Site, Announcement, JoinRequest, Worker
from transactions.models import MilkSupplyRecord, MilkSaleRecord, Expense, MilkLoss
from transactions.forms import MilkSupplyForm, MilkSaleForm, ExpenseForm, MilkLossForm
from training.models import TrainingResource, SystemUpdate, MilkStandard
from communication.models import ChatMessage, Notification
from users.models import User

from business.serializers import SiteSerializer, SupplierSerializer, BuyerSerializer, WorkerSerializer
from transactions.serializers import MilkSupplyRecordSerializer

class SiteDetailView(LoginRequiredMixin, DetailView):
    model = Site; template_name = "site_detail.html"; context_object_name = "site"; login_url = "/admin/login/"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); user, today = self.request.user, timezone.now().date()
        try: year, month = int(self.request.GET.get('year', today.year)), int(self.request.GET.get('month', today.month))
        except ValueError: year, month = today.year, today.month
        prev_month, prev_year = (month - 1 if month > 1 else 12), (year if month > 1 else year - 1)
        next_month, next_year = (month + 1 if month < 12 else 1), (year if month < 12 else year + 1)
        suppliers = self.object.suppliers.all().order_by('name'); _, num_days = calendar.monthrange(year, month); days = list(range(1, num_days + 1))
        records = MilkSupplyRecord.objects.filter(site=self.object, date__year=year, date__month=month); data_map = {}
        for r in records:
            if r.supplier_id not in data_map: data_map[r.supplier_id] = {}
            data_map[r.supplier_id][r.date.day] = float(r.litres)
        supplier_data = []
        for s in suppliers:
            day_values = []
            for day in days:
                can_edit = True
                if user.role == User.MANAGER:
                    perms = getattr(user, 'manager_permissions', None); is_today = (year == today.year and month == today.month and day == today.day)
                    if not is_today: can_edit = perms.can_edit_past_dates if perms else False
                elif user.role != User.SUPER_ADMIN: can_edit = False
                day_values.append({'day': day, 'litres': data_map.get(s.id, {}).get(day, ''), 'can_edit': can_edit})
            supplier_data.append({'id': s.id, 'name': s.name, 'days': day_values})
        context.update({'supplier_data': supplier_data, 'days': days, 'month_name': calendar.month_name[month], 'current_year': year, 'current_month': month, 'prev_month': prev_month, 'prev_year': prev_year, 'next_month': next_month, 'next_year': next_year, 'today_day': today.day if today.year == year and today.month == month else 0})
        return context

@method_decorator(csrf_exempt, name='dispatch')
class SaveMilkRecordView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.role not in [User.SUPER_ADMIN, User.MANAGER]: return JsonResponse({'status': 'error', 'message': 'Denied'}, status=403)
        try:
            data = json.loads(request.body); supplier_id, site_id, day, month, year, litres = data.get('supplier_id'), data.get('site_id'), int(data.get('day')), int(data.get('month')), int(data.get('year')), data.get('litres')
            if user.role == User.MANAGER:
                today = timezone.now().date()
                if not (year == today.year and month == today.month and day == today.day):
                    perms = getattr(user, 'manager_permissions', None)
                    if not perms or not perms.can_edit_past_dates: return JsonResponse({'status': 'error', 'message': 'Today only'}, status=403)
            date_obj = timezone.make_aware(timezone.datetime(year, month, day))
            record = MilkSupplyRecord.objects.filter(supplier_id=supplier_id, site_id=site_id, date__year=year, date__month=month, date__day=day).first()
            if litres is None or litres == '' or float(litres) == 0:
                if record: record.delete()
                return JsonResponse({'status': 'deleted'})
            if not record: record = MilkSupplyRecord(supplier_id=supplier_id, site_id=site_id, date=date_obj, price_per_litre=500)
            record.litres = float(litres); record.save()
            return JsonResponse({'status': 'success', 'total': float(record.total_cost)})
        except Exception as e: return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm; template_name = 'change_password.html'; success_url = reverse_lazy('user_profile'); login_url = "/admin/login/"
    def form_valid(self, form): messages.success(self.request, "Updated!"); return super().form_valid(form)

def login_success(request):
    user = request.user
    return redirect('dashboard') if user.role in ['SUPER_ADMIN', 'MANAGER'] else redirect('user_profile')

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"; login_url = "/admin/login/"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); user = self.request.user
        context.update({'total_supplied': 0, 'total_bought': 0, 'records': [], 'profile': None, 'profile_type': user.get_role_display()})
        if user.role == User.SUPPLIER:
            profile = getattr(user, 'supplier_profile', None)
            if profile:
                context['profile'] = profile; context['records'] = MilkSupplyRecord.objects.filter(supplier=profile).order_by('-date')
                context['total_supplied'] = context['records'].aggregate(Sum('litres'))['litres__sum'] or 0
        elif user.role == User.BUYER:
            profile = getattr(user, 'buyer_profile', None)
            if profile:
                context['profile'] = profile; context['records'] = MilkSaleRecord.objects.filter(buyer=profile).order_by('-date')
                context['total_bought'] = context['records'].aggregate(Sum('litres'))['litres__sum'] or 0
        elif user.role in [User.MANAGER, User.SUPER_ADMIN]:
            perms = getattr(user, 'manager_permissions', None)
            if perms and perms.assigned_site: context['assigned_site'] = perms.assigned_site
        return context

def supplier_report(request, pk):
    if request.user.role not in ['SUPER_ADMIN', 'MANAGER'] and (request.user.role == 'SUPPLIER' and request.user.supplier_profile.id != pk):
        return redirect('home')
    supplier = get_object_or_404(Supplier, pk=pk); records = MilkSupplyRecord.objects.filter(supplier=supplier).order_by('-date')
    return render(request, 'reports/statement.html', {'title': 'Supplier Statement', 'owner': supplier, 'records': records, 'total_litres': records.aggregate(Sum('litres'))['litres__sum'] or 0, 'total_value': records.aggregate(Sum('total_cost'))['total_cost__sum'] or 0, 'today': timezone.now()})

def buyer_report(request, pk):
    if request.user.role not in ['SUPER_ADMIN', 'MANAGER'] and (request.user.role == 'BUYER' and request.user.buyer_profile.id != pk):
        return redirect('home')
    buyer = get_object_or_404(Buyer, pk=pk); records = MilkSaleRecord.objects.filter(buyer=buyer).order_by('-date')
    return render(request, 'reports/statement.html', {'title': 'Buyer Statement', 'owner': buyer, 'records': records, 'total_litres': records.aggregate(Sum('litres'))['litres__sum'] or 0, 'total_value': records.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0, 'today': timezone.now()})

class LandingPageView(TemplateView):
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'announcements': Announcement.objects.filter(is_active=True).order_by('-created_at')[:3], 'milk_standard': MilkStandard.objects.all().order_by('-effective_date').first()})
        return context

class JoinRequestView(CreateView):
    model = JoinRequest; fields = ['name', 'phone', 'email', 'password', 'request_type', 'message']; template_name = "home.html"; success_url = reverse_lazy('home')
    def form_valid(self, form):
        obj = form.save(); admins = User.objects.filter(role='SUPER_ADMIN')
        for admin in admins: Notification.objects.create(user=admin, title=f"New {obj.request_type} Request", message=f"{obj.name} wants to join. Phone: {obj.phone}", link="/dashboard/")
        messages.success(self.request, "Partnership request sent successfully! We will review it soon."); return super().form_valid(form)

class JoinRequestListView(LoginRequiredMixin, ListView):
    model = JoinRequest; template_name = "join_requests.html"; context_object_name = "requests"; login_url = "/admin/login/"
    def get_queryset(self):
        if self.request.user.role != 'SUPER_ADMIN': return JoinRequest.objects.none()
        return JoinRequest.objects.filter(status='PENDING').order_by('-created_at')

def process_join_request(request, pk, action):
    if request.user.role != 'SUPER_ADMIN': return redirect('home')
    join_req = get_object_or_404(JoinRequest, pk=pk)
    if action == 'accept':
        username = join_req.name.lower().replace(' ', '_')
        if User.objects.filter(username=username).exists(): username = f"{username}_{timezone.now().strftime('%M%S')}"
        role = User.SUPPLIER if join_req.request_type == 'SUPPLIER' else User.BUYER
        # Create user with the password they chose in the request
        user = User.objects.create_user(username=username, email=join_req.email, password=join_req.password, role=role)
        user.is_staff = True; user.save()
        if role == User.SUPPLIER: Supplier.objects.create(user=user, name=join_req.name, contact=join_req.phone)
        else: Buyer.objects.create(user=user, name=join_req.name, contact=join_req.phone)
        join_req.status = 'APPROVED'; join_req.save()
        messages.success(request, f"Approved! User: {username} can now login with their chosen password.")
    else: join_req.status = 'REJECTED'; join_req.save(); messages.info(request, "Request ignored.")
    return redirect('dashboard')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"; login_url = "/admin/login/"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); user, today = self.request.user, timezone.now().date()
        week_start, month_start = today - timedelta(days=today.weekday()), today.replace(day=1)
        supply_qs, sale_qs, expense_qs, loss_qs = MilkSupplyRecord.objects.all(), MilkSaleRecord.objects.all(), Expense.objects.all(), MilkLoss.objects.all()
        can_see_revenue = (user.role == User.SUPER_ADMIN)
        if user.role == User.MANAGER:
            perms = getattr(user, 'manager_permissions', None); can_see_revenue = perms.can_see_revenue if perms else False
        
        context.update({'can_see_revenue': can_see_revenue, 'milk_today': supply_qs.filter(date__date=today).aggregate(Sum('litres'))['litres__sum'] or 0, 'loss_today': loss_qs.filter(date=today).aggregate(Sum('litres'))['litres__sum'] or 0})
        
        if can_see_revenue:
            context.update({'revenue_today': sale_qs.filter(date__date=today).aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0, 'cost_today': supply_qs.filter(date__date=today).aggregate(Sum('total_cost'))['total_cost__sum'] or 0, 'expenses_today': expense_qs.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0})
            context['profit_today'] = context['revenue_today'] - (context['cost_today'] + context['expenses_today'])
            context['revenue_month'] = sale_qs.filter(date__date__gte=month_start).aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
        else: context.update({'revenue_today': "Restricted", 'profit_today': "Restricted", 'revenue_month': 0})
        
        context.update({
            'milk_week': supply_qs.filter(date__date__gte=week_start).aggregate(Sum('litres'))['litres__sum'] or 0, 
            'milk_month': supply_qs.filter(date__date__gte=month_start).aggregate(Sum('litres'))['litres__sum'] or 0, 
            'active_suppliers_count': supply_qs.filter(date__date=today).values('supplier').distinct().count(), 
            'expense_form': ExpenseForm(), 
            'loss_form': MilkLossForm(),
            'pending_requests': JoinRequest.objects.filter(status='PENDING').order_by('-created_at') if user.role == User.SUPER_ADMIN else [],
            'unread_notifications': Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:5]
        })
        
        site_stats = []
        for site in Site.objects.all():
            collected = supply_qs.filter(site=site, date__date=today).aggregate(Sum('litres'))['litres__sum'] or 0
            site_stats.append({'id': site.id, 'name': site.name, 'collected': float(collected)})
        context['site_stats'] = site_stats; return context

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user, today = request.user, timezone.now().date(); week_start = today - timedelta(days=today.weekday())
        supply_qs, sale_qs, expense_qs, loss_qs = MilkSupplyRecord.objects.all(), MilkSaleRecord.objects.all(), Expense.objects.all(), MilkLoss.objects.all()
        can_see_revenue = (user.role == User.SUPER_ADMIN)
        if user.role == User.MANAGER: perms = getattr(user, 'manager_permissions', None); can_see_revenue = perms.can_see_revenue if perms else False
        data = {'milk_today': supply_qs.filter(date__date=today).aggregate(Sum('litres'))['litres__sum'] or 0, 'loss_today': loss_qs.filter(date=today).aggregate(Sum('litres'))['litres__sum'] or 0, 'milk_week': supply_qs.filter(date__date__gte=week_start).aggregate(Sum('litres'))['litres__sum'] or 0, 'can_see_revenue': can_see_revenue}
        if can_see_revenue:
            rev_today, cost_today, exp_today = (sale_qs.filter(date__date=today).aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0), (supply_qs.filter(date__date=today).aggregate(Sum('total_cost'))['total_cost__sum'] or 0), (expense_qs.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0)
            data.update({'revenue_today': float(rev_today), 'profit_today': float(rev_today - (cost_today + exp_today)), 'expenses_today': float(exp_today)})
        return Response(data)

class SiteListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        sites = Site.objects.all(); serializer = SiteSerializer(sites, many=True); return Response(serializer.data)

class SiteDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        site = get_object_or_404(Site, pk=pk); today = timezone.now().date(); records = MilkSupplyRecord.objects.filter(site=site, date__date=today)
        return Response({'site': SiteSerializer(site).data, 'today_records': MilkSupplyRecordSerializer(records, many=True).data})

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user; data = {'username': user.username, 'role': user.role, 'email': user.email}
        if user.role == 'SUPPLIER':
            profile = getattr(user, 'supplier_profile', None)
            if profile: data['profile'] = SupplierSerializer(profile).data
        elif user.role == 'BUYER':
            profile = getattr(user, 'buyer_profile', None)
            if profile: data['profile'] = BuyerSerializer(profile).data
        return Response(data)

class TrainingView(LoginRequiredMixin, TemplateView):
    template_name = "training.html"; login_url = "/admin/login/"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'resources': TrainingResource.objects.all().order_by('-created_at'), 'updates': SystemUpdate.objects.filter(is_active=True).order_by('-date'), 'standards': MilkStandard.objects.all().order_by('-effective_date').first()})
        return context

class TrainingResourceCreateView(LoginRequiredMixin, CreateView):
    model = TrainingResource; fields = ['title', 'description', 'content', 'file']; success_url = reverse_lazy('training')
    def form_valid(self, form):
        if self.request.user.role != User.SUPER_ADMIN: return redirect('training')
        form.instance.author = self.request.user; messages.success(self.request, "Lesson uploaded!"); return super().form_valid(form)

class TrainingResourceDeleteView(LoginRequiredMixin, DeleteView):
    model = TrainingResource; success_url = reverse_lazy('training')
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.SUPER_ADMIN: return redirect('training')
        return super().dispatch(request, *args, **kwargs)

class ChatView(LoginRequiredMixin, TemplateView):
    template_name = "chat.html"; login_url = "/admin/login/"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['chat_users'] = User.objects.exclude(id=self.request.user.id); return context

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification; template_name = "notifications.html"; context_object_name = "notifications"; login_url = "/admin/login/"
    def get_queryset(self): return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class SiteListView(LoginRequiredMixin, ListView):
    model = Site; template_name = "sites.html"; context_object_name = "sites"; login_url = "/admin/login/"
    def get_queryset(self):
        user, sites = self.request.user, list(Site.objects.all())
        for site in sites:
            site.total_collected = MilkSupplyRecord.objects.filter(site=site).aggregate(Sum('litres'))['litres__sum'] or 0
            site.total_sold = MilkSaleRecord.objects.filter(site_source=site).aggregate(Sum('litres'))['litres__sum'] or 0
            site.net_flow = site.total_collected - site.total_sold
            can_see = (user.role == User.SUPER_ADMIN) or (user.role == User.MANAGER and getattr(user.manager_permissions, 'can_see_revenue', False))
            site.total_revenue = MilkSaleRecord.objects.filter(site_source=site).aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0 if can_see else "Hidden"
        return sites

class WorkerListView(LoginRequiredMixin, ListView):
    model = Worker; template_name = "workers.html"; context_object_name = "workers"; login_url = "/admin/login/"
    def get_queryset(self): return Worker.objects.all()

class CreateWorkerView(LoginRequiredMixin, CreateView):
    model = Worker; fields = ['name', 'role', 'base_pay']; success_url = reverse_lazy('worker_list')
    def form_valid(self, form):
        if self.request.user.role != User.SUPER_ADMIN: messages.error(self.request, "Denied."); return self.form_invalid(form)
        username = form.cleaned_data['name'].lower().replace(' ', '_'); 
        if User.objects.filter(username=username).exists(): username = f"{username}_{timezone.now().strftime('%M%S')}"
        new_user = User.objects.create_user(username=username, password='password123', role=User.WORKER); new_user.is_staff = True; new_user.save(); form.instance.user = new_user
        messages.success(self.request, f"Worker added!"); return super().form_valid(form)

class WorkerDeleteView(LoginRequiredMixin, DeleteView):
    model = Worker; success_url = reverse_lazy('worker_list')
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.SUPER_ADMIN: return redirect('worker_list')
        return super().dispatch(request, *args, **kwargs)

def pay_worker(request, pk):
    if request.user.role != 'SUPER_ADMIN': return redirect('worker_list')
    worker = get_object_or_404(Worker, pk=pk); amount = request.POST.get('amount')
    if amount: messages.success(request, f"Paid RWF {amount} to {worker.name} successfully!")
    return redirect('worker_list')

from users.models import ManagerPermission
class ManagerListView(LoginRequiredMixin, ListView):
    model = User; template_name = "managers.html"; context_object_name = "managers"; login_url = "/admin/login/"
    def get_queryset(self): return User.objects.filter(role=User.MANAGER).select_related('manager_permissions', 'manager_permissions__assigned_site')
    def get_context_data(self, **kwargs): context = super().get_context_data(**kwargs); context['sites'] = Site.objects.all(); return context

class ManagerCreateView(LoginRequiredMixin, CreateView):
    model = User; fields = ['username', 'email', 'password']; success_url = reverse_lazy('manager_list')
    def form_valid(self, form):
        if self.request.user.role != User.SUPER_ADMIN: return redirect('manager_list')
        user = form.save(commit=False); user.role = User.MANAGER; user.is_staff = True; user.set_password(form.cleaned_data['password']); user.save()
        site_id = self.request.POST.get('assigned_site'); site = Site.objects.get(id=site_id) if site_id else None
        ManagerPermission.objects.create(user=user, assigned_site=site, can_see_revenue=self.request.POST.get('can_see_revenue') == 'on', can_edit_past_dates=self.request.POST.get('can_edit_past_dates') == 'on')
        messages.success(self.request, "Manager created!"); return redirect('manager_list')

class ManagerDeleteView(LoginRequiredMixin, DeleteView):
    model = User; success_url = reverse_lazy('manager_list')
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.SUPER_ADMIN: return redirect('manager_list')
        return super().dispatch(request, *args, **kwargs)

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier; template_name = "suppliers.html"; context_object_name = "suppliers"; login_url = "/admin/login/"
    def get_queryset(self):
        user, qs = self.request.user, super().get_queryset()
        if user.role == User.MANAGER:
            perms = getattr(user, 'manager_permissions', None); 
            if perms and perms.assigned_site: qs = qs.filter(site=perms.assigned_site)
        return qs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); user = self.request.user; sites = Site.objects.all()
        if user.role == User.MANAGER:
            perms = getattr(user, 'manager_permissions', None); 
            if perms and perms.assigned_site: sites = sites.filter(id=perms.assigned_site.id)
        context['sites'] = sites; return context

class CreateSupplierView(LoginRequiredMixin, CreateView):
    model = Supplier; fields = ['name', 'contact', 'site']; success_url = reverse_lazy('supplier_list')
    def form_valid(self, form):
        user = self.request.user
        if user.role == User.MANAGER:
            perms = getattr(user, 'manager_permissions', None); 
            if perms and perms.assigned_site and form.cleaned_data['site'] != perms.assigned_site:
                messages.error(self.request, "Denied."); return self.form_invalid(form)
        username = form.cleaned_data['name'].lower().replace(' ', '_'); 
        if User.objects.filter(username=username).exists(): username = f"{username}_{timezone.now().strftime('%M%S')}"
        new_user = User.objects.create_user(username=username, password='password123', role=User.SUPPLIER); new_user.is_staff = True; new_user.save(); form.instance.user = new_user
        messages.success(self.request, f"Supplier added!"); return super().form_valid(form)

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier; fields = ['name', 'contact', 'site']; template_name = "supplier_form.html"; success_url = reverse_lazy('supplier_list')
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.SUPER_ADMIN: return redirect('supplier_list')
        return super().dispatch(request, *args, **kwargs)

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier; success_url = reverse_lazy('supplier_list')
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.SUPER_ADMIN: return redirect('supplier_list')
        return super().dispatch(request, *args, **kwargs)

class BuyerListView(LoginRequiredMixin, ListView):
    model = Buyer; template_name = "buyers.html"; context_object_name = "buyers"; login_url = "/admin/login/"

class CreateBuyerView(LoginRequiredMixin, CreateView):
    model = Buyer; fields = ['name', 'contact']; success_url = reverse_lazy('buyer_list')
    def form_valid(self, form):
        username = form.cleaned_data['name'].lower().replace(' ', '_'); 
        if User.objects.filter(username=username).exists(): username = f"{username}_{timezone.now().strftime('%M%S')}"
        new_user = User.objects.create_user(username=username, password='password123', role=User.BUYER); new_user.is_staff = True; new_user.save(); form.instance.user = new_user
        messages.success(self.request, f"Buyer added!"); return super().form_valid(form)

class BuyerUpdateView(LoginRequiredMixin, UpdateView):
    model = Buyer; fields = ['name', 'contact']; template_name = "buyer_form.html"; success_url = reverse_lazy('buyer_list')
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.SUPER_ADMIN: return redirect('buyer_list')
        return super().dispatch(request, *args, **kwargs)

class BuyerDeleteView(LoginRequiredMixin, DeleteView):
    model = Buyer; success_url = reverse_lazy('buyer_list')
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.SUPER_ADMIN: return redirect('buyer_list')
        return super().dispatch(request, *args, **kwargs)

class TransactionListView(LoginRequiredMixin, TemplateView):
    template_name = "transactions.html"; login_url = "/admin/login/"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); user = self.request.user; supplies, sales = MilkSupplyRecord.objects.all().order_by('-date'), MilkSaleRecord.objects.all().order_by('-date')
        if user.role == User.MANAGER:
            perms = getattr(user, 'manager_permissions', None); 
            if perms and perms.assigned_site: supplies, sales = supplies.filter(site=perms.assigned_site), sales.filter(site_source=perms.assigned_site)
        context.update({'supplies': supplies, 'sales': sales, 'supply_form': MilkSupplyForm(), 'sale_form': MilkSaleForm()}); return context

class RecordSupplyView(LoginRequiredMixin, CreateView):
    model = MilkSupplyRecord; form_class = MilkSupplyForm; success_url = reverse_lazy('transaction_list')
    def form_valid(self, form):
        user = self.request.user
        if user.role == User.MANAGER:
            perms = getattr(user, 'manager_permissions', None)
            if perms and perms.assigned_site and form.cleaned_data['site'] != perms.assigned_site:
                messages.error(self.request, "Unauthorized site."); return self.form_invalid(form)
            if form.cleaned_data.get('date') and form.cleaned_data['date'].date() != timezone.now().date():
                if not perms or not perms.can_edit_past_dates: messages.error(self.request, "Today only."); return self.form_invalid(form)
        response = super().form_valid(form); supplier = self.object.supplier; supplier.current_balance += self.object.total_cost; supplier.save()
        messages.success(self.request, f"Supply recorded!"); return response

class RecordSaleView(LoginRequiredMixin, CreateView):
    model = MilkSaleRecord; form_class = MilkSaleForm; success_url = reverse_lazy('transaction_list')
    def form_valid(self, form):
        user = self.request.user
        if user.role == User.MANAGER:
            perms = getattr(user, 'manager_permissions', None)
            if perms and perms.assigned_site and form.cleaned_data['site_source'] != perms.assigned_site:
                messages.error(self.request, "Unauthorized site."); return self.form_invalid(form)
            if form.cleaned_data.get('date') and form.cleaned_data['date'].date() != timezone.now().date():
                if not perms or not perms.can_edit_past_dates: messages.error(self.request, "Today only."); return self.form_invalid(form)
        response = super().form_valid(form); buyer = self.object.buyer; buyer.current_balance += self.object.total_revenue; buyer.save()
        messages.success(self.request, f"Sale recorded!"); return response

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense; form_class = ExpenseForm; success_url = reverse_lazy('dashboard')
    def form_valid(self, form):
        if self.request.user.role == User.MANAGER:
            perms = getattr(self.request.user, 'manager_permissions', None)
            if perms and perms.assigned_site and form.cleaned_data['site'] != perms.assigned_site:
                messages.error(self.request, "Unauthorized site."); return self.form_invalid(form)
        messages.success(self.request, "Expense recorded!"); return super().form_valid(form)

class MilkLossCreateView(LoginRequiredMixin, CreateView):
    model = MilkLoss; form_class = MilkLossForm; success_url = reverse_lazy('dashboard')
    def form_valid(self, form):
        if self.request.user.role == User.MANAGER:
            perms = getattr(self.request.user, 'manager_permissions', None)
            if perms and perms.assigned_site and form.cleaned_data['site'] != perms.assigned_site:
                messages.error(self.request, "Unauthorized site."); return self.form_invalid(form)
        messages.success(self.request, "Loss recorded!"); return super().form_valid(form)
