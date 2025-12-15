from django import forms
from .models import Product, Order, Customer, Category, MaterialType, MaterialPricing


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'product_type', 'price', 'cost', 'quantity', 'min_quantity', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
            'product_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_product_type'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_cost'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_quantity'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_min_quantity'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show rental categories when product type is rental
        self.fields['category'].queryset = Category.objects.filter(name__in=['Barong', 'Suits', 'Coat', 'Pants'])
        self.fields['category'].required = False  # Make category optional initially
        
        # Override product_type choices to only show Rental Item
        self.fields['product_type'].choices = [('rental', 'Rental Item')]
        self.fields['product_type'].initial = 'rental'  # Set default to rental
    
    def clean(self):
        cleaned_data = super().clean()
        product_type = cleaned_data.get('product_type')
        category = cleaned_data.get('category')
        
        if product_type == 'rental' and not category:
            raise forms.ValidationError('Category is required for rental items.')
        
        # Set default values for rental items
        if product_type == 'rental':
            cleaned_data['cost'] = 0  # No cost price for rental items
            cleaned_data['quantity'] = 1  # Default quantity for rental items
            cleaned_data['min_quantity'] = 0  # No minimum quantity for rental items
        
        return cleaned_data


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'order_type', 'notes', 'due_date']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'order_type': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def save(self, commit=True):
        order = super().save(commit=False)
        # Set status to 'rented' for rental orders
        if order.order_type in ['rent', 'rental']:
            order.status = 'rented'
        if commit:
            order.save()
        return order


class MaterialTypeForm(forms.ModelForm):
    class Meta:
        model = MaterialType
        fields = ['name', 'description', 'unit_of_measurement', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_of_measurement': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MaterialPricingForm(forms.ModelForm):
    class Meta:
        model = MaterialPricing
        fields = ['material_type', 'pricing_type', 'bundle_size', 'buy_price_per_unit', 'sell_price_per_unit', 'is_default']
        widgets = {
            'material_type': forms.Select(attrs={'class': 'form-control'}),
            'pricing_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_pricing_type'}),
            'bundle_size': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_bundle_size', 'min': '1'}),
            'buy_price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sell_price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make bundle_size required only for per_bundle pricing
        self.fields['bundle_size'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        pricing_type = cleaned_data.get('pricing_type')
        bundle_size = cleaned_data.get('bundle_size')
        
        if pricing_type == 'per_bundle' and not bundle_size:
            raise forms.ValidationError('Bundle size is required for per bundle pricing.')
        
        return cleaned_data


class MaterialProductForm(forms.ModelForm):
    """Form for creating material products with dynamic fields based on material type"""
    
    # Basic fields
    # Use ModelChoiceField to work with MaterialType objects directly
    material_type = forms.ModelChoiceField(
        queryset=MaterialType.objects.exclude(name__iexact='locks').exclude(name__iexact='elastic').order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_material_type'}),
        required=True,
        empty_label='Select Material Type',
    )
    
    # Selling price field (common for all)
    selling_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_selling_price'}),
        required=False,
        help_text="Selling price"
    )
    
    # Legacy fields - kept for backward compatibility but not used in new structure
    quantity_type = forms.ChoiceField(
        choices=[
            ('per_piece', 'Per Piece'),
            ('per_group', 'Per Group'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_quantity_type', 'style': 'display: none;'}),
        required=False,
        initial='per_piece'
    )
    
    cost_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'style': 'display: none;'}),
        required=False,
        help_text="Cost price per unit"
    )
    
    # Dynamic fields for Locks/Kawit
    locks_type = forms.ChoiceField(
        choices=[
            ('', 'Select Type'),
            ('normal', 'Normal'),
            ('special', 'Special'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_locks_type'}),
        required=False
    )
    
    locks_cost_per_meters = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_locks_cost_per_meters'}),
        required=False
    )
    
    locks_selling_price_per_group = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '14.00', 'id': 'id_locks_selling_price_per_group'}),
        required=False,
        help_text="Default: ₱14 per group (4 pieces)"
    )
    
    # Dynamic fields for Zippers
    zipper_color = forms.ChoiceField(
        choices=[
            ('', 'Select Color'),
            ('black', 'Black'),
            ('white', 'White'),
            ('other', 'Other Color'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_zipper_color'}),
        required=False
    )
    
    zipper_color_other = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter other color', 'id': 'id_zipper_color_other'}),
        required=False
    )
    
    zipper_length_cm = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_zipper_length_cm'}),
        required=False
    )
    
    zipper_type = forms.ChoiceField(
        choices=[
            ('', 'Select Type'),
            ('normal', 'Normal'),
            ('special', 'Special'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_zipper_type'}),
        required=False
    )
    
    zipper_cost_per_centimeters = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_zipper_cost_per_centimeters'}),
        required=False
    )
    
    zipper_selling_price_per_centimeters = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_zipper_selling_price_per_centimeters'}),
        required=False
    )
    
    # Dynamic fields for Needles
    needle_size = forms.ChoiceField(
        choices=[
            ('', 'Select Size'),
            ('60/8', '60/8'),
            ('65/9', '65/9'),
            ('70/10', '70/10'),
            ('75/11', '75/11'),
            ('50/12', '50/12'),
            ('90/14', '90/14'),
            ('100/16', '100/16'),
            ('110/18', '110/18'),
            ('120/19', '120/19'),
            ('130/21', '130/21'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_needle_size'}),
        required=False
    )
    
    needle_cost_per_bundle = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_needle_cost_per_bundle'}),
        required=False
    )
    
    needle_selling_price_per_bundle = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_needle_selling_price_per_bundle'}),
        required=False
    )
    
    # Dynamic fields for Patches
    patch_type = forms.ChoiceField(
        choices=[
            ('', 'Select Type'),
            ('normal', 'Normal'),
            ('logo', 'Logo'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_patch_type'}),
        required=False
    )
    
    patch_size = forms.ChoiceField(
        choices=[
            ('', 'Select Size'),
            ('small', 'Small'),
            ('medium', 'Medium'),
            ('large', 'Large'),
            ('xl', 'XL'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_patch_size'}),
        required=False
    )
    
    patch_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_patch_cost'}),
        required=False
    )
    
    patch_selling_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_patch_selling_price'}),
        required=False
    )
    
    # Dynamic fields for Buttons
    button_type = forms.ChoiceField(
        choices=[
            ('', 'Select Button Type'),
            ('plastic', 'Plastic'),
            ('metal', 'Metal'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_button_type'}),
        required=False
    )
    
    button_brand = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter brand', 'id': 'id_button_brand'}),
        required=False
    )
    
    button_color = forms.ChoiceField(
        choices=[
            ('', 'Select Color'),
            ('black', 'Black'),
            ('white', 'White'),
            ('assorted', 'Assorted'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_button_color'}),
        required=False
    )
    
    button_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_button_cost'}),
        required=False
    )
    
    button_quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': '0', 'id': 'id_button_quantity'}),
        required=False
    )
    
    button_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_button_price'}),
        required=False
    )
    
    button_selling_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_button_selling_price'}),
        required=False
    )
    
    button_price_per = forms.ChoiceField(
        choices=[
            ('', 'Select'),
            ('group', 'Group'),
            ('pieces', 'Pieces'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_button_price_per'}),
        required=False
    )
    
    # Dynamic fields for Fabric
    fabric_type = forms.ChoiceField(
        choices=[
            ('', 'Select Fabric Type'),
            ('linen', 'Linen'),
            ('cotton', 'Cotton'),
            ('silk', 'Silk'),
            ('wool', 'Wool'),
            ('cashmere', 'Cashmere'),
            ('hemp', 'Hemp'),
            ('jute', 'Jute'),
            ('polyester', 'Polyester'),
            ('nylon', 'Nylon'),
            ('acrylic', 'Acrylic'),
            ('rayon', 'Rayon'),
            ('spandex', 'Spandex'),
            ('acetate', 'Acetate'),
            ('denim', 'Denim'),
            ('corduroy', 'Corduroy'),
            ('cotton_polyester', 'Cotton-Polyester'),
            ('wool_nylon', 'Wool-Nylon'),
            ('rayon_spandex', 'Rayon-Spandex'),
            ('knitted_fabrics', 'Knitted Fabrics'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_fabric_type'}),
        required=False
    )
    
    fabric_yard = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_fabric_yard'}),
        required=False
    )
    
    fabric_cost_per_yard = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_fabric_cost_per_yard'}),
        required=False
    )
    
    fabric_selling_price_per_yard = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_fabric_selling_price_per_yard'}),
        required=False
    )
    
    fabric_color = forms.ChoiceField(
        choices=[
            ('', 'Select Color'),
            ('black', 'Black'),
            ('white', 'White'),
            ('red', 'Red'),
            ('blue', 'Blue'),
            ('green', 'Green'),
            ('yellow', 'Yellow'),
            ('orange', 'Orange'),
            ('pink', 'Pink'),
            ('purple', 'Purple'),
            ('brown', 'Brown'),
            ('gray', 'Gray'),
            ('grey', 'Grey'),
            ('navy', 'Navy'),
            ('maroon', 'Maroon'),
            ('beige', 'Beige'),
            ('cream', 'Cream'),
            ('khaki', 'Khaki'),
            ('indigo', 'Indigo'),
            ('teal', 'Teal'),
            ('add_another_color', 'Add Another Color'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_fabric_color'}),
        required=False
    )
    
    fabric_custom_color = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter custom color', 'id': 'id_fabric_custom_color', 'style': 'display: none;'}),
        required=False
    )
    
    # Dynamic fields for Garter
    garter_length_cm = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_garter_length_cm'}),
        required=False
    )
    
    garter_cost_per_cm = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_garter_cost_per_cm'}),
        required=False
    )
    
    garter_selling_price_per_cm = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_garter_selling_price_per_cm'}),
        required=False
    )
    
    # Dynamic fields for Thread
    thread_brand = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter brand', 'id': 'id_thread_brand'}),
        required=False
    )
    
    thread_color = forms.ChoiceField(
        choices=[
            ('', 'Select Color'),
            ('black', 'Black'),
            ('white', 'White'),
            ('blue', 'Blue'),
            ('yellow', 'Yellow'),
            ('green', 'Green'),
            ('brown', 'Brown'),
            ('violet', 'Violet'),
            ('pink', 'Pink'),
            ('gray', 'Gray'),
            ('gold', 'Gold'),
            ('orange', 'Orange'),
            ('assorted', 'Assorted'),
            ('other', 'Other / Add New Color'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_thread_color'}),
        required=False
    )
    
    thread_color_other = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter custom color name', 'id': 'id_thread_color_other'}),
        required=False,
        help_text="Enter a custom color name"
    )
    
    thread_length = forms.ChoiceField(
        choices=[
            ('', 'Select Length'),
            ('500', '500m'),
            ('1000', '1000m'),
            ('1500', '1500m'),
            ('2000', '2000m'),
            ('2500', '2500m'),
            ('3000', '3000m'),
            ('3500', '3500m'),
            ('4000', '4000m'),
            ('4500', '4500m'),
            ('5000', '5000m'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_thread_length'}),
        required=False
    )
    
    thread_cost_per_meters = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_thread_cost_per_meters'}),
        required=False
    )
    
    thread_selling_price_per_meters = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_thread_selling_price_per_meters'}),
        required=False
    )
    
    # Brand field (common for all)
    brand = forms.ChoiceField(
        choices=[
            ('normal', 'Normal'),
            ('apple', 'Apple'),
            ('add_new', 'Add Another Brand'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_brand'}),
        required=False
    )
    
    custom_brand = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter custom brand name'}),
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['name', 'quantity', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter material name', 'id': 'id_name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0', 'id': 'id_quantity'}),
            'image': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*', 
                'id': 'id_image',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set labels
        self.fields['name'].label = "Material Name"
        self.fields['quantity'].label = "Quantity"
        self.fields['quantity'].required = False  # Make quantity optional since some materials handle it differently
        # Remove quantity_type and cost_price from __init__ since they're not used in the new structure
    
    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('material_type')
        quantity = cleaned_data.get('quantity')
        
        # Validate quantity
        if quantity is not None and quantity < 0:
            self.add_error('quantity', 'Quantity must be 0 or greater.')
        
        # Validate material-specific fields based on material type
        if material_type:
            if material_type == 'buttons':
                button_type = cleaned_data.get('button_type')
                button_brand = cleaned_data.get('button_brand')
                button_color = cleaned_data.get('button_color')
                button_cost = cleaned_data.get('button_cost')
                quantity = cleaned_data.get('quantity', 0) or 0
                button_selling_price = cleaned_data.get('button_selling_price')
                
                if not button_type:
                    self.add_error('button_type', 'Button type is required.')
                if not button_brand:
                    self.add_error('button_brand', 'Brand is required for buttons.')
                if not button_color:
                    self.add_error('button_color', 'Color is required for buttons.')
                if not button_cost or button_cost <= 0:
                    self.add_error('button_cost', 'Cost per Group is required and must be greater than zero.')
                if not quantity or quantity <= 0:
                    self.add_error('quantity', 'Quantity (pcs) is required and must be greater than zero.')
                if not button_selling_price or button_selling_price <= 0:
                    self.add_error('button_selling_price', 'Selling Price Per Group is required and must be greater than zero.')
            
            elif material_type == 'fabric':
                fabric_type = cleaned_data.get('fabric_type')
                fabric_yard = cleaned_data.get('fabric_yard')
                fabric_cost_per_yard = cleaned_data.get('fabric_cost_per_yard')
                fabric_selling_price_per_yard = cleaned_data.get('fabric_selling_price_per_yard')
                
                if not fabric_type:
                    self.add_error('fabric_type', 'Type of fabric is required.')
                if not fabric_yard or fabric_yard <= 0:
                    self.add_error('fabric_yard', 'Yard is required and must be greater than zero.')
                if not fabric_cost_per_yard or fabric_cost_per_yard <= 0:
                    self.add_error('fabric_cost_per_yard', 'Cost per yard is required and must be greater than zero.')
                if not fabric_selling_price_per_yard or fabric_selling_price_per_yard <= 0:
                    self.add_error('fabric_selling_price_per_yard', 'Selling price per yard is required and must be greater than zero.')
                
                # Validate custom color if "Add Another Color" is selected
                fabric_color = cleaned_data.get('fabric_color', '')
                fabric_custom_color = cleaned_data.get('fabric_custom_color', '')
                if fabric_color == 'add_another_color':
                    if not fabric_custom_color or not fabric_custom_color.strip():
                        self.add_error('fabric_custom_color', 'Custom color is required when "Add Another Color" is selected.')
            
            elif material_type == 'garter':
                garter_length_cm = cleaned_data.get('garter_length_cm')
                garter_cost_per_cm = cleaned_data.get('garter_cost_per_cm')
                garter_selling_price_per_cm = cleaned_data.get('garter_selling_price_per_cm')
                
                if not garter_length_cm or garter_length_cm <= 0:
                    self.add_error('garter_length_cm', 'Garter length (inch) is required and must be greater than zero.')
                if not garter_cost_per_cm or garter_cost_per_cm <= 0:
                    self.add_error('garter_cost_per_cm', 'Cost per inches is required and must be greater than zero.')
                if not garter_selling_price_per_cm or garter_selling_price_per_cm <= 0:
                    self.add_error('garter_selling_price_per_cm', 'Selling price per inches is required and must be greater than zero.')
            
            elif material_type == 'thread':
                thread_brand = cleaned_data.get('thread_brand')
                thread_color = cleaned_data.get('thread_color')
                thread_color_other = cleaned_data.get('thread_color_other', '').strip()
                thread_length = cleaned_data.get('thread_length')
                thread_cost_per_meters = cleaned_data.get('thread_cost_per_meters')
                thread_selling_price_per_meters = cleaned_data.get('thread_selling_price_per_meters')
                thread_quantity = cleaned_data.get('quantity', 0) or 0
                
                if not thread_brand:
                    self.add_error('thread_brand', 'Brand is required for thread.')
                if not thread_color:
                    self.add_error('thread_color', 'Color is required for thread.')
                # If "other" color is selected, require custom color name
                if thread_color == 'other' and not thread_color_other:
                    self.add_error('thread_color_other', 'Custom color name is required when "Other / Add New Color" is selected.')
                if not thread_length:
                    self.add_error('thread_length', 'Length is required for thread.')
                if not thread_quantity or thread_quantity <= 0:
                    self.add_error('quantity', 'Quantity (meters) is required and must be greater than zero for thread.')
                if not thread_cost_per_meters or thread_cost_per_meters <= 0:
                    self.add_error('thread_cost_per_meters', 'Cost per meters is required and must be greater than zero.')
                if not thread_selling_price_per_meters or thread_selling_price_per_meters <= 0:
                    self.add_error('thread_selling_price_per_meters', 'Selling price per meters is required and must be greater than zero.')
            
            elif material_type == 'locks_kawit':
                locks_type = cleaned_data.get('locks_type')
                locks_cost_per_meters = cleaned_data.get('locks_cost_per_meters')
                locks_selling_price_per_group = cleaned_data.get('locks_selling_price_per_group')
                
                if not locks_type:
                    self.add_error('locks_type', 'Type is required for locks/kawit.')
                if not locks_cost_per_meters or locks_cost_per_meters <= 0:
                    self.add_error('locks_cost_per_meters', 'Cost per group is required and must be greater than zero.')
                if not locks_selling_price_per_group or locks_selling_price_per_group <= 0:
                    self.add_error('locks_selling_price_per_group', 'Selling price per group (₱14 for 4 pieces) is required and must be greater than zero.')
            
            elif material_type == 'zippers':
                zipper_color = cleaned_data.get('zipper_color')
                zipper_length_cm = cleaned_data.get('zipper_length_cm')
                zipper_type = cleaned_data.get('zipper_type')
                zipper_cost_per_centimeters = cleaned_data.get('zipper_cost_per_centimeters')
                zipper_selling_price_per_centimeters = cleaned_data.get('zipper_selling_price_per_centimeters')
                
                if not zipper_color:
                    self.add_error('zipper_color', 'Color is required for zippers.')
                if zipper_color == 'other' and not cleaned_data.get('zipper_color_other'):
                    self.add_error('zipper_color_other', 'Please enter the other color.')
                if not zipper_length_cm or zipper_length_cm <= 0:
                    self.add_error('zipper_length_cm', 'Length (cm) is required and must be greater than zero.')
                if not zipper_type:
                    self.add_error('zipper_type', 'Type is required for zippers.')
                if not zipper_cost_per_centimeters or zipper_cost_per_centimeters <= 0:
                    self.add_error('zipper_cost_per_centimeters', 'Cost per centimeters is required and must be greater than zero.')
                if not zipper_selling_price_per_centimeters or zipper_selling_price_per_centimeters <= 0:
                    self.add_error('zipper_selling_price_per_centimeters', 'Selling price per centimeters is required and must be greater than zero.')
            
            elif material_type == 'needles':
                needle_size = cleaned_data.get('needle_size')
                needle_cost_per_bundle = cleaned_data.get('needle_cost_per_bundle')
                needle_selling_price_per_bundle = cleaned_data.get('needle_selling_price_per_bundle')
                
                if not needle_size:
                    self.add_error('needle_size', 'Size is required for needles.')
                if not needle_cost_per_bundle or needle_cost_per_bundle <= 0:
                    self.add_error('needle_cost_per_bundle', 'Cost per bundle is required and must be greater than zero.')
                if not needle_selling_price_per_bundle or needle_selling_price_per_bundle <= 0:
                    self.add_error('needle_selling_price_per_bundle', 'Selling price per bundle is required and must be greater than zero.')
            
            elif material_type == 'patches':
                patch_type = cleaned_data.get('patch_type')
                patch_size = cleaned_data.get('patch_size')
                patch_cost = cleaned_data.get('patch_cost')
                patch_selling_price = cleaned_data.get('patch_selling_price')
                
                if not patch_type:
                    self.add_error('patch_type', 'Type is required for patches.')
                if not patch_size:
                    self.add_error('patch_size', 'Size is required for patches.')
                if not patch_cost or patch_cost <= 0:
                    self.add_error('patch_cost', 'Cost is required and must be greater than zero.')
                if not patch_selling_price or patch_selling_price <= 0:
                    self.add_error('patch_selling_price', 'Selling price is required and must be greater than zero.')
        
        return cleaned_data
    
    def save(self, commit=True):
        from decimal import Decimal, InvalidOperation
        
        # Helper function to safely convert to Decimal
        def safe_decimal(value, default=Decimal('0.00')):
            """Safely convert value to Decimal, handling empty strings and None"""
            if value is None or value == '':
                return default
            try:
                if isinstance(value, Decimal):
                    return value
                return Decimal(str(value))
            except (ValueError, InvalidOperation, TypeError):
                return default
        
        product = super().save(commit=False)
        material_type_obj = self.cleaned_data.get('material_type')
        
        # Set material_type if provided (now it's a MaterialType object directly)
        if material_type_obj:
            product.material_type = material_type_obj
        
        # Get material type name for conditional logic (use lowercase for matching)
        material_type_name = material_type_obj.name.lower() if material_type_obj else ''
        
        # Calculate cost and price based on material type
        cost = Decimal('0.00')
        price = Decimal('0.00')
        quantity = self.cleaned_data.get('quantity', 0) or 0
        description_parts = []
        unit_of_measurement = 'piece'
        
        if material_type_name == 'buttons' or (material_type_obj and 'button' in material_type_name):
            cost = safe_decimal(self.cleaned_data.get('button_cost', 0))
            price = safe_decimal(self.cleaned_data.get('button_selling_price', 0))
            # Use quantity from main field
            quantity = self.cleaned_data.get('quantity', 0) or 0
            unit_of_measurement = 'pieces'
            
            description_parts.append(f"Button Type: {self.cleaned_data.get('button_type', '').title()}")
            description_parts.append(f"Brand: {self.cleaned_data.get('button_brand', '')}")
            description_parts.append(f"Color: {self.cleaned_data.get('button_color', '').title()}")
            description_parts.append(f"Cost per Group: ₱{cost}")
            description_parts.append(f"Selling Price Per Group: ₱{price}")
        
        elif material_type_name == 'fabric' or (material_type_obj and 'fabric' in material_type_name):
            fabric_yard = self.cleaned_data.get('fabric_yard', 0) or 0
            cost = safe_decimal(self.cleaned_data.get('fabric_cost_per_yard', 0))
            price = safe_decimal(self.cleaned_data.get('fabric_selling_price_per_yard', 0))
            quantity = int(fabric_yard)
            unit_of_measurement = 'yard'
            
            # Handle fabric color - use custom color if "add_another_color" is selected
            fabric_color_value = self.cleaned_data.get('fabric_color', '')
            if fabric_color_value == 'add_another_color':
                fabric_color_display = self.cleaned_data.get('fabric_custom_color', '').strip().title()
            else:
                fabric_color_display = fabric_color_value.title() if fabric_color_value else ''
            
            description_parts.append(f"Type of Fabric: {self.cleaned_data.get('fabric_type', '').replace('_', '-').title()}")
            if fabric_color_display:
                description_parts.append(f"Color: {fabric_color_display}")
            description_parts.append(f"Yard: {fabric_yard}")
            description_parts.append(f"Cost per yard: ₱{cost}")
            description_parts.append(f"Selling price per yard: ₱{price}")
        
        elif material_type_name == 'garter' or (material_type_obj and 'garter' in material_type_name):
            garter_length = self.cleaned_data.get('garter_length_cm', 0) or 0
            cost = safe_decimal(self.cleaned_data.get('garter_cost_per_cm', 0))
            price = safe_decimal(self.cleaned_data.get('garter_selling_price_per_cm', 0))
            quantity = int(garter_length)
            unit_of_measurement = 'inches'  # Garter uses inches
            
            description_parts.append(f"Garter length: {garter_length} inch")
            description_parts.append(f"Cost per inches: ₱{cost}")
            description_parts.append(f"Selling price per inches: ₱{price}")
        
        elif material_type_name == 'thread' or (material_type_obj and 'thread' in material_type_name):
            cost = safe_decimal(self.cleaned_data.get('thread_cost_per_meters', 0))
            price = safe_decimal(self.cleaned_data.get('thread_selling_price_per_meters', 0))
            # Get quantity and ensure it's a valid integer
            quantity_value = self.cleaned_data.get('quantity', 0) or 0
            quantity = int(float(quantity_value)) if quantity_value else 0  # Convert to integer for Thread quantity in meters
            unit_of_measurement = 'meters'
            
            # Handle thread color - use custom color if "other" is selected
            thread_color_value = self.cleaned_data.get('thread_color', '')
            if thread_color_value == 'other':
                thread_color_display = self.cleaned_data.get('thread_color_other', '').strip().title()
            else:
                thread_color_display = thread_color_value.title() if thread_color_value else ''
            
            description_parts.append(f"Brand: {self.cleaned_data.get('thread_brand', '')}")
            description_parts.append(f"Color: {thread_color_display}")
            description_parts.append(f"Length: {self.cleaned_data.get('thread_length', '')}m")
            description_parts.append(f"Cost per meters: ₱{cost}")
            description_parts.append(f"Selling price per meters: ₱{price}")
        
        elif material_type_name in ['locks/kawit', 'locks_kawit', 'locks', 'kawit'] or (material_type_obj and ('lock' in material_type_name or 'kawit' in material_type_name)):
            cost = safe_decimal(self.cleaned_data.get('locks_cost_per_meters', 0))
            price = safe_decimal(self.cleaned_data.get('locks_selling_price_per_group', 0))
            quantity = self.cleaned_data.get('quantity', 0) or 0  # Use form quantity or default to 0
            unit_of_measurement = 'group'  # Each group consists of 4 pieces
            
            description_parts.append(f"Type: {self.cleaned_data.get('locks_type', '').title()}")
            description_parts.append(f"Group size: 4 pieces per group")
            description_parts.append(f"Cost per group: ₱{cost}")
            description_parts.append(f"Selling price per group: ₱{price}")
        
        elif material_type_name == 'zippers' or (material_type_obj and 'zipper' in material_type_name):
            zipper_length = self.cleaned_data.get('zipper_length_cm', 0) or 0
            cost = safe_decimal(self.cleaned_data.get('zipper_cost_per_centimeters', 0))
            price = safe_decimal(self.cleaned_data.get('zipper_selling_price_per_centimeters', 0))
            quantity = int(zipper_length)
            unit_of_measurement = 'inches'  # Zippers use inches
            
            zipper_color = self.cleaned_data.get('zipper_color', '')
            if zipper_color == 'other':
                zipper_color = self.cleaned_data.get('zipper_color_other', '')
            
            description_parts.append(f"Color: {zipper_color.title()}")
            description_parts.append(f"Length: {zipper_length} inch")
            description_parts.append(f"Type: {self.cleaned_data.get('zipper_type', '').title()}")
            description_parts.append(f"Cost per inches: ₱{cost}")
            description_parts.append(f"Selling price per inches: ₱{price}")
        
        elif material_type_name == 'needles' or (material_type_obj and 'needle' in material_type_name):
            cost = safe_decimal(self.cleaned_data.get('needle_cost_per_bundle', 0))
            price = safe_decimal(self.cleaned_data.get('needle_selling_price_per_bundle', 0))
            quantity = self.cleaned_data.get('quantity', 0) or 0  # Use form quantity or default to 0
            unit_of_measurement = 'bundle'
            
            description_parts.append(f"Size: {self.cleaned_data.get('needle_size', '')}")
            description_parts.append(f"Cost per bundle: ₱{cost}")
            description_parts.append(f"Selling price per bundle: ₱{price}")
        
        elif material_type_name == 'patches' or (material_type_obj and 'patch' in material_type_name):
            cost = safe_decimal(self.cleaned_data.get('patch_cost', 0))
            price = safe_decimal(self.cleaned_data.get('patch_selling_price', 0))
            quantity = self.cleaned_data.get('quantity', 0) or 0  # Use form quantity or default to 0
            unit_of_measurement = 'piece'
            
            description_parts.append(f"Type: {self.cleaned_data.get('patch_type', '').title()}")
            description_parts.append(f"Size: {self.cleaned_data.get('patch_size', '').title()}")
            description_parts.append(f"Cost: ₱{cost}")
            description_parts.append(f"Selling price: ₱{price}")
        
        # Set product fields
        product.product_type = 'material'  # Ensure product_type is set to 'material'
        product.cost = cost
        product.price = price
        product.quantity = quantity
        product.unit_of_measurement = unit_of_measurement
        product.min_quantity = 0
        product.description = "; ".join(description_parts)
        product.is_active = True  # Ensure material is active by default
        product.is_archived = False  # Ensure material is not archived
        
        # Set current_quantity_in_stock to match quantity for new materials
        if not product.pk:
            product.current_quantity_in_stock = quantity
        
        # Handle image uploads
        # Get all uploaded images
        image_files = self.files.getlist('image')
        
        if image_files and len(image_files) > 0 and image_files[0]:
            # Save the first image as the primary product image
            try:
                product.image = image_files[0]
                image_name = getattr(image_files[0], 'name', 'unknown')
                image_size = getattr(image_files[0], 'size', 0)
                print(f"[MATERIAL DEBUG] Primary image uploaded: {image_name} ({image_size} bytes)")
            except Exception as e:
                print(f"[MATERIAL DEBUG] Error setting image: {e}")
                # Continue without image if there's an error
        
        if commit:
            # Update MaterialType unit_of_measurement if needed
            if product.material_type and product.material_type.unit_of_measurement != unit_of_measurement:
                product.material_type.unit_of_measurement = unit_of_measurement
                product.material_type.save()
            
            product.save()
        
        return product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UniformMeasurementForm(forms.Form):
    """Form for collecting uniform measurements for custom tailoring"""
    
    # Customize a - FIRST FIELD
    customize_a = forms.ChoiceField(
        choices=[
            ('', 'Select Type'),
            ('uniform', 'Uniform'),
            ('pe', 'PE'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_customize_a', 'required': True}),
        required=True,
        label='Customize a'
    )
    
    # Gender Selection (only for Uniform)
    gender = forms.ChoiceField(
        choices=[
            ('', 'Select Gender'),
            ('male', 'Male'),
            ('female', 'Female'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_gender'}),
        required=False,
        label='Gender'
    )
    
    # Customization Type (for Uniform)
    customization_type = forms.ChoiceField(
        choices=[
            ('', 'Select Customization'),
            ('pants', 'Pants'),
            ('polo', 'Polo'),
            ('blouse', 'Blouse'),
            ('skirt_palda', 'Skirt/Palda'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_customization_type'}),
        required=False,
        label='Customization Type'
    )
    
    # PE Down Type
    pe_down_type = forms.ChoiceField(
        choices=[
            ('', 'Select PE Down Type'),
            ('short', 'Short'),
            ('pants', 'Pants'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_pe_down_type'}),
        required=False,
        label='PE Down Type'
    )
    
    # Female Bottom Type
    female_bottom_type = forms.ChoiceField(
        choices=[
            ('', 'Select Bottom Type'),
            ('pants', 'Pants'),
            ('skirt', 'Skirt'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_female_bottom_type'}),
        required=False,
        label='Bottom Type'
    )
    
    # MALE POLO/SHIRT SIZES
    male_neck = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(13, 19)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Neck (inches)'
    )
    
    male_shoulder = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(16, 22)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Shoulder (inches)'
    )
    
    male_chest = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(34, 47, 2)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Chest (inches)'
    )
    
    male_waist_shirt = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(28, 43, 2)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Waist (inches)'
    )
    
    male_hip_shirt = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(34, 51)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Hip (inches)'
    )
    
    male_armhole = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(16, 25)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Armhole (inches)'
    )
    
    male_sleeve_length = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(18, 29)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Sleeve Length (inches)'
    )
    
    male_bicep = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(10, 19)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Bicep (inches)'
    )
    
    male_wrist = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(6, 13)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Wrist (inches)'
    )
    
    male_shirt_length = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(24, 35)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Shirt Length (inches)'
    )
    
    # MALE PANTS SIZES
    male_pants_waist = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(28, 51)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Waist (inches)'
    )
    
    male_pants_hip = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(34, 51)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Hip (inches)'
    )
    
    male_rise = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(9, 16)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Rise (inches)'
    )
    
    male_thigh = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(18, 31)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Thigh (inches)'
    )
    
    male_knee = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(14, 23)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Knee (inches)'
    )
    
    male_leg_opening = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(12, 21)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Leg Opening (inches)'
    )
    
    male_inseam = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(28, 35)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Inseam (inches)'
    )
    
    male_outseam = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(34, 41)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Outseam / Pants Length (inches)'
    )
    
    # FEMALE BLOUSE/TOP SIZES
    female_neck = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(12, 19)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Neck (inches)'
    )
    
    female_shoulder = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(14, 21)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Shoulder (inches)'
    )
    
    female_bust = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(30, 51)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Bust (inches)'
    )
    
    female_underbust = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(26, 45)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Underbust (inches)'
    )
    
    female_waist_top = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(24, 45)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Waist (inches)'
    )
    
    female_hip_top = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(30, 51)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Hip (inches)'
    )
    
    female_armhole = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(14, 23)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Armhole (inches)'
    )
    
    female_sleeve_length = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(16, 27)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Sleeve Length (inches)'
    )
    
    female_bicep = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(10, 19)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Bicep (inches)'
    )
    
    female_wrist = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(5, 11)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Wrist (inches)'
    )
    
    female_blouse_length = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(22, 33)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Blouse Length (inches)'
    )
    
    # FEMALE PANTS SIZES
    female_pants_waist = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(24, 45)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Waist (inches)'
    )
    
    female_pants_hip = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(30, 51)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Hip (inches)'
    )
    
    female_rise = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(8, 13)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Rise (inches)'
    )
    
    female_thigh = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(18, 29)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Thigh (inches)'
    )
    
    female_knee = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(13, 21)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Knee (inches)'
    )
    
    female_leg_opening = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(11, 19)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Leg Opening (inches)'
    )
    
    female_inseam = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(26, 35)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Inseam (inches)'
    )
    
    female_outseam = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(34, 41)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Outseam / Length (inches)'
    )
    
    # FEMALE SKIRT SIZES
    female_skirt_waist = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(24, 45)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Waist (inches)'
    )
    
    female_skirt_hip = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(30, 51)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Hip (inches)'
    )
    
    female_skirt_length = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(18, 29)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Skirt Length (inches)'
    )
    
    female_hem_width = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(28, 51)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Hem Width (inches)'
    )
    
    # PE SHORTS Fields
    pe_short_waist = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter waist size'}),
        required=False,
        label='Waist (Gar garter)'
    )
    
    pe_short_hips = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hips size'}),
        required=False,
        label='Hips'
    )
    
    pe_short_length = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter shorts length'}),
        required=False,
        label='Shorts Length'
    )
    
    # PE PANTS Fields
    pe_pants_waist = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter waist size'}),
        required=False,
        label='Waist (Gar garter)'
    )
    
    pe_pants_hips = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hips size'}),
        required=False,
        label='Hips'
    )
    
    pe_pants_length = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pants length'}),
        required=False,
        label='Pants Length'
    )
    
    pe_pants_leg_opening = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter leg opening'}),
        required=False,
        label='Leg Opening / Hem'
    )
    
    pe_pants_inseam = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter inseam'}),
        required=False,
        label='Inseam (Inner leg length)'
    )
    
    pe_pants_outseam = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter outseam'}),
        required=False,
        label='Outseam / Full Length'
    )
    
    # PE T-SHIRT Fields
    pe_tshirt_size = forms.ChoiceField(
        choices=[('', 'Select Size')] + [('xs', 'XS'), ('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL'), ('2xl', '2XL'), ('3xl', '3XL')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='T-shirt Size'
    )
    
    pe_tshirt_size_custom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter custom size'}),
        required=False,
        label='Custom Size'
    )
    
    pe_chest_circumference = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(34, 47, 2)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Chest Circumference'
    )
    
    pe_chest_circumference_custom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter custom chest size'}),
        required=False,
        label='Custom Chest'
    )
    
    pe_shirt_length = forms.ChoiceField(
        choices=[('', 'Select')] + [(str(i), str(i)) for i in range(24, 29)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Shirt Length'
    )
    
    pe_shirt_length_custom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter custom length'}),
        required=False,
        label='Custom Length'
    )
    
    pe_neck_circumference = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter neck circumference'}),
        required=False,
        label='Neck Circumference'
    )
    
    pe_bust = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter bust size'}),
        required=False,
        label='Bust'
    )
    
    pe_armhole = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter armhole size'}),
        required=False,
        label='Armhole'
    )
    
    pe_shoulder = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter shoulder size'}),
        required=False,
        label='Shoulder'
    )
    
    pe_tshirt_waist = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter waist size'}),
        required=False,
        label='Waist'
    )
    
    # Uniform Pants - Checkbox fields with custom input
    uniform_pants_waist_checkbox = forms.MultipleChoiceField(
        choices=[(str(i), str(i)) for i in range(28, 51)],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Waist Size (Checkboxes)'
    )
    
    uniform_pants_waist_custom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Or enter custom waist size'}),
        required=False,
        label='Custom Waist Size'
    )
    
    uniform_pants_hips_checkbox = forms.MultipleChoiceField(
        choices=[(str(i), str(i)) for i in range(30, 51)],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Hips Size (Checkboxes)'
    )
    
    uniform_pants_hips_custom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Or enter custom hips size'}),
        required=False,
        label='Custom Hips Size'
    )
    
    uniform_pants_inseam_checkbox = forms.MultipleChoiceField(
        choices=[(str(i), str(i)) for i in range(30, 36)],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Inseam Size (Checkboxes)'
    )
    
    uniform_pants_inseam_custom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Or enter custom inseam size'}),
        required=False,
        label='Custom Inseam Size'
    )
    
    # Uniform Polo - Checkbox fields with custom input
    uniform_polo_chest_checkbox = forms.MultipleChoiceField(
        choices=[(str(i), str(i)) for i in range(30, 51)],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Chest Size (Checkboxes)'
    )
    
    uniform_polo_chest_custom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Or enter custom chest size'}),
        required=False,
        label='Custom Chest Size'
    )
    
    uniform_polo_shoulder_checkbox = forms.MultipleChoiceField(
        choices=[(str(i), str(i)) for i in range(17, 23)],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Shoulder Size (Checkboxes)'
    )
    
    uniform_polo_shoulder_custom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Or enter custom shoulder size'}),
        required=False,
        label='Custom Shoulder Size'
    )
    
    uniform_polo_shirt_length_checkbox = forms.MultipleChoiceField(
        choices=[(str(i), str(i)) for i in range(26, 31)],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Shirt Length Size (Checkboxes)'
    )
    
    uniform_polo_shirt_length_custom = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Or enter custom shirt length'}),
        required=False,
        label='Custom Shirt Length'
    )
    
    # Uniform Blouse - Sleeve and measurements
    uniform_blouse_sleeve = forms.ChoiceField(
        choices=[
            ('', 'Select Sleeve Type'),
            ('short', 'Short'),
            ('3/4', '3/4'),
            ('long', 'Long'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_uniform_blouse_sleeve'}),
        required=False,
        label='Sleeve Type'
    )
    
    uniform_blouse_sleeve_length_short = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter sleeve length'}),
        required=False,
        label='Sleeve Length (Short)'
    )
    
    uniform_blouse_sleeve_length_34 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter sleeve length'}),
        required=False,
        label='Sleeve Length (3/4)'
    )
    
    uniform_blouse_sleeve_length_long = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter sleeve length'}),
        required=False,
        label='Sleeve Length (Long)'
    )
    
    uniform_blouse_shoulder_width = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter shoulder width'}),
        required=False,
        label='Shoulder Width'
    )
    
    uniform_blouse_bust = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter bust measurement'}),
        required=False,
        label='Bust'
    )
    
    uniform_blouse_under_bust = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter under bust measurement'}),
        required=False,
        label='Under Bust'
    )
    
    uniform_blouse_waist = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter waist measurement'}),
        required=False,
        label='Waist'
    )
    
    uniform_blouse_hip = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hip measurement'}),
        required=False,
        label='Hip'
    )
    
    uniform_blouse_neck = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter neck measurement'}),
        required=False,
        label='Neck'
    )
    
    uniform_blouse_armhole = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter armhole measurement'}),
        required=False,
        label='Armhole'
    )
    
    uniform_blouse_length = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter blouse length'}),
        required=False,
        label='Blouse Length'
    )
    
    # Uniform Skirt/Palda
    uniform_skirt_waist = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter waist measurement'}),
        required=False,
        label='Waist'
    )
    
    uniform_skirt_hips = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hips measurement'}),
        required=False,
        label='Hips'
    )
    
    uniform_skirt_length = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter skirt length'}),
        required=False,
        label='Skirt Length'
    )
    
    uniform_skirt_hem_width = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hem width'}),
        required=False,
        label='Hem Width'
    )
    
    # Additional Notes
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes or special instructions...'}),
        required=False,
        label='Additional Notes'
    )

