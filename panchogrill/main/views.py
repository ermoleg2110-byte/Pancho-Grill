from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm
from .models import CartItem, Category, ContactInfo, MenuItem, Promo


def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _build_context():
    categories = Category.objects.prefetch_related("menu_items")
    contacts = ContactInfo.objects.first()
    featured_items = MenuItem.objects.select_related("category")[:8]
    promos = Promo.objects.all()
    cart_items = CartItem.objects.select_related("menu_item")

    return {
        "categories": categories,
        "promos": promos,
        "contacts": contacts,
        "featured_items": featured_items,
        "cart_items": cart_items,
    }


def home(request):
    context = _build_context()
    context["page_title"] = "Главная"
    return render(request, "home.html", context)


def menu(request):
    context = _build_context()
    context["page_title"] = "Меню"
    return render(request, "menu.html", context)


def cart(request):
    context = _build_context()
    context["page_title"] = "Корзина"
    context["cart_total"] = sum(item.qty * item.price for item in context["cart_items"])
    if context["cart_total"] != 0 and context["cart_total"] >= 1200:
        context["discount"] = context["cart_total"] * 0.1
        context["result"] = context["cart_total"] - context["discount"]
    return render(request, "cart.html", context)


@login_required
def checkout(request):
    context = _build_context()
    context["page_title"] = "Оформление заказа"
    context["cart_total"] = sum(item.qty * item.price for item in context["cart_items"])
    if context["cart_total"] != 0 and context["cart_total"] >= 1200:
        context["discount"] = context["cart_total"] * 0.1
        context["result"] = context["cart_total"] - context["discount"]
    return render(request, "checkout.html", context)


def contacts(request):
    context = _build_context()
    context["page_title"] = "Контакты"
    return render(request, "contacts.html", context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Вы успешно вошли в аккаунт.')
        next_url = request.GET.get('next') or request.POST.get('next')
        return redirect(next_url or 'home')

    return render(request, 'login.html', { 'form': form })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Аккаунт успешно создан. Добро пожаловать!')
        return redirect('home')

    return render(request, 'register.html', { 'form': form })


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('home')


def add_to_cart(request, item_id):
    if request.method == "POST":
        session_key = _get_session_key(request)
        menu_item = get_object_or_404(MenuItem, id=item_id)

        cart_item, created = CartItem.objects.get_or_create(
            session_key=session_key,
            menu_item=menu_item,
            defaults={"qty": 1},
        )

        if not created:
            cart_item.qty += 1
            cart_item.save()

    return redirect("cart")


def change_cart_qty(request, item_id, action):
    if request.method == "POST":
        session_key = _get_session_key(request)
        cart_item = get_object_or_404(
            CartItem,
            session_key=session_key,
            menu_item_id=item_id,
        )

        if action == "plus":
            cart_item.qty += 1
            cart_item.save()
        elif action == "minus":
            if cart_item.qty > 1:
                cart_item.qty -= 1
                cart_item.save()
            else:
                cart_item.delete()

    return redirect("cart")


def remove_from_cart(request, item_id):
    if request.method == "POST":
        session_key = _get_session_key(request)
        CartItem.objects.filter(
            session_key=session_key,
            menu_item_id=item_id,
        ).delete()

    return redirect("cart")