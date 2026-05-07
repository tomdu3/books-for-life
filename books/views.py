from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.utils.text import slugify
from django.db.models import Q
from .models import Book, Category
from .forms import BookForm


def home(request):
    """Render the home page."""
    return render(request, 'books/home.html')


@login_required
def user_page(request):
    """Render the user's personal page displaying their books."""
    user = request.user

    user_books = Book.objects.filter(user_id=user.id)
    context = {
        'user': user,
        'books': user_books,
    }
    return render(request, 'books/user_page.html', context=context)


def book_delete_confirmation(request, book_id):
    """Confirm and handle the deletion of a book by ID."""
    book = get_object_or_404(Book, id=book_id)

    if book.user_id != request.user:
        messages.error(request, 'You do not have permission to delete this book.')
        return redirect('user_page')

    if request.method == 'POST':
        # Handle the actual deletion of the book here
        book.delete()
        messages.success(request, f'Book "{book.title}" successfully deleted!', extra_tags='success')
        return redirect('user_page')

    return render(request, 'books/book_delete.html', {'book': book})


class BookDetail(LoginRequiredMixin, View):
    """Display the details of a specific book."""

    def get(self, request, slug, *args, **kwargs):
        queryset = Book.objects.all()
        book = get_object_or_404(queryset, slug=slug)

        # the control field for the like button
        liked_by_user = False
        if book.likes.filter(id=request.user.id).exists():
            liked_by_user = True

        context = {
            'book': book,
            'liked_by_user': liked_by_user,
        }
        return render(request, 'books/book_detail.html', context=context)


@login_required
def user_favourites(request):
    """Render the user's favourite books page."""
    user = request.user

    liked_books = Book.objects.filter(likes=user)
    context = {
        'user': user,
        'books': liked_books,
    }
    return render(request, 'books/user_favourites.html', context=context)


class BookUpdateView(LoginRequiredMixin, View):
    """View for updating an existing book."""
    def get(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        if book.user_id != request.user:
            messages.error(request, 'You do not have permission to edit this book.')
            return redirect('user_page')
        
        form = BookForm(instance=book)
        categories = Category.objects.all()
        book.short_description = book.short_description.strip()
        context = {
            'book': book,
            'form': form,
            'categories': categories,
        }
        return render(request, 'books/book_edit.html', context)

    def post(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        if book.user_id != request.user:
            messages.error(request, 'You do not have permission to edit this book.')
            return redirect('user_page')
            
        categories = Category.objects.all()
        form = BookForm(request.POST, request.FILES, instance=book)

        if form.is_valid():
            # Save the form to update the Book instance
            form.save()

            # Success message upon update
            messages.success(
                request,
                (f'Book "{book.title}" successfully updated!'),
                extra_tags='success')
            return redirect('user_page')

        messages.error(request, 'Please correct the errors below.', extra_tags='danger')
        context = {
            'book': book,
            'form': form,
            'categories': categories,
        }
        return render(request, 'books/book_edit.html', context)


class AddBookView(LoginRequiredMixin, View):
    """View for adding a new book."""
    def get(self, request):
        form = BookForm()
        categories = Category.objects.all()

        context = {
            'form': form,
            'categories': categories,
        }
        return render(request, 'books/book_add.html', context)

    def post(self, request):
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user  # Get the current user

            # Extract cleaned data from the form
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            short_description = form.cleaned_data['short_description']
            full_description = form.cleaned_data['full_description']
            image_url = form.cleaned_data['image_url']
            category_name = form.cleaned_data['category']
            # Get the category instance based on the category name
            category = Category.objects.get(name=category_name)

            # Generate a slug based on the title
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            # Check if a record with the same slug already exists and apply
            # a counter to add to the text slug if it does
            while Book.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            # Create and save the Book instance
            book = Book(
                title=title,
                author=author,
                short_description=short_description,
                full_description=full_description,
                image_url=image_url,
                category=category,
                slug=slug,
                user_id=user,
            )
            book.save()

            # Success message upon creation
            messages.success(
                request,
                (f'Book "{book.title}" successfully added!'),
                extra_tags='success')
            return redirect('user_page')

        messages.error(request, 'Please correct the errors below.', extra_tags='danger')
        categories = Category.objects.all()

        context = {
            'form': form,
            'categories': categories,
        }
        return render(request, 'books/book_add.html', context)


class BookDeleteView(LoginRequiredMixin, View):
    """View for handling the deletion of a book by slug."""
    def get(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        
        if book.user_id != request.user:
            messages.error(request, 'You do not have permission to delete this book.')
            return redirect('user_page')
            
        book.delete()

        # Success message upon deletion
        messages.success(
            request,
            (f'Book "{book.title}" successfully deleted!'),
            extra_tags='success'
        )

        return redirect('user_page')


@login_required
def find_book(request):
    """View for searching and displaying books."""

    query = request.GET.get('q')  # Get the query parameter from the URL
    if query:
        # Search for books that match the query in title, author or category
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query) |
            Q(category__name__icontains=query))
    else:
        # If no query is provided, display all books
        books = Book.objects.all()

    # Add a control field value to each book liked by user
    for book in books:
        if book.likes.filter(id=request.user.id).exists():
            book.liked_by_user = True

    context = {
        'books': books,
    }
    return render(request, 'books/find_book.html', context=context)


@login_required
def like_book(request, slug):
    """Handle liking/unliking a book from the find_book view."""
    query_param = request.POST.get('q')  # Get the query parameter from the URL
    print(query_param)

    if request.method == 'POST' and request.user.is_authenticated:
        book = get_object_or_404(Book, slug=slug)

        # Check if the user has already liked the book
        liked_by_user = book.likes.filter(id=request.user.id).exists()

        if liked_by_user:
            # User has already liked the book, remove the like
            book.likes.remove(request.user)
        else:
            # User hasn't liked the book, add the like
            book.likes.add(request.user)

    # Redirect back to the 'find_book' view with the previous query parameter
    if query_param:
        return redirect(reverse('find_book') + f'?q={query_param}')
    else:
        return redirect('find_book')


@login_required
def like_book_detail(request, slug):
    """Handle liking/unliking a book from the book detail view."""
    if request.method == 'POST' and request.user.is_authenticated:
        book = get_object_or_404(Book, slug=slug)

        # Check if the user has already liked the book
        liked_by_user = book.likes.filter(id=request.user.id).exists()

        if liked_by_user:
            # User has already liked the book, remove the like
            book.likes.remove(request.user)
        else:
            # User hasn't liked the book, add the like
            book.likes.add(request.user)

        # Redirect back to the book detail page
        return redirect('book_detail', slug=slug)


def remove_from_favourites(request, slug):
    """Remove a book from the user's favourites."""
    user = request.user

    # Get the book by its slug
    book = get_object_or_404(Book, slug=slug)

    # Check if the user has liked the book
    if user in book.likes.all():
        book.likes.remove(user)  # Remove the user from the book's likes

    # Redirect back to the user's favourites page
    return redirect('user_favourites')
