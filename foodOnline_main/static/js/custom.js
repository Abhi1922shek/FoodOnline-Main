let autocomplete;

function initAutoComplete() {
    // console.log('Initializing Autocomplete...');
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('id_address'),
        {
            types: ['geocode', 'establishment'],
            componentRestrictions: { 'country': ['in'] },
        }
    );
    autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged() {
    var place = autocomplete.getPlace();
    // console.log('Place changed:', place);

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry) {
        document.getElementById('id_address').placeholder = "Start typing...";
    } else {
        console.log('Selected place:', place);
    }

    // get the address components and assign them to the fields
    var geocoder = new google.maps.Geocoder();
    var address = document.getElementById('id_address').value;
    // console.log('Geocoding address:', address);
    
    geocoder.geocode({ 'address': address }, function(results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();
            console.log('latitude:', latitude);
            console.log('longitude:', longitude);

            // jQuery
            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);
            $('#id_address').val(address);
        } else {
            console.error('Geocoding failed:', status);
        }
    });
    console.log(place.address_components)
    // loop through the address components and assign other address data
    for (var i = 0; i < place.address_components.length; i++) {
        for (var j = 0; j < place.address_components[i].types.length; j++) {
            //country
            if (place.address_components[i].types[j] === 'country') {
                $('#id_country').val(place.address_components[i].long_name);
            }
            //state
            if (place.address_components[i].types[j] === 'administrative_area_level_1') {
                $('#id_state').val(place.address_components[i].long_name);
            }
            //city
            if (place.address_components[i].types[j] === 'locality') {
                $('#id_city').val(place.address_components[i].long_name);
                console.log(place.address_components[i].types[j])
            }
            //pincode
            if (place.address_components[i].types[j] === 'postal_code') {
                $('#id_pin_code').val(place.address_components[i].long_name);
            } else {
                $('#id_pin_code').val('');
            }
        }
    }
}

// jQuery
$(document).ready(function(){
    // ADD to cart
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        // AJAX requests
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                // console.log(response);
                if (response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login/';
                    })
                }else if (response.status == 'Failed'){
                    swal(response.message, '', 'error');
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)

                    // subtotal, tax, total functionality
                    applyCartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['total']
                    )
                }
            }
        })
    })

    // place the item quantity on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id');
        var qty = $(this).attr('data-qty');
        $('#'+the_id).html(qty)
    })

    // DECREASE from cart
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');
        // AJAX requests
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response);
                if (response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login/';
                    })
                }else if (response.status == 'Failed'){
                    swal(response.message, '', 'error');
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)

                    // subtotal, tax, total functionality
                    applyCartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['total']
                    )

                    if (window.location.pathname == '/cart/'){
                        removeCartItem(response.qty, cart_id);
                        checkEmptyCart()                    
                    }

                }
            }
        })
    })

    // delete cart item
    $('.delete_cart').on('click', function(e){
        e.preventDefault();
        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        // AJAX requests
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response);
                if (response.status == 'Failed'){
                    swal(response.message, '', 'error');
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    swal(response.status, response.message, 'success');

                    // subtotal, tax, total functionality
                    applyCartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['total']
                    )
                    
                    removeCartItem(0, cart_id);
                    checkEmptyCart()
                }
            }
        })
    })

    // delete the cart element if the qty is 0
    function removeCartItem(cartItemQty, cart_id){
        if (cartItemQty <= 0){
            // remove cart item element
            document.getElementById("cart-item-"+cart_id).remove()
        }
    }

    // check for empty cart
    function checkEmptyCart(){
        if ($('#cart_counter').html() == 0){
            var cart_counter = document.getElementById('cart_counter').innerHTML
            if (cart_counter == 0){
                document.getElementById('empty-cart').style.display = 'block'
            }
        }
    }

    // apply cart amount functionality

    function applyCartAmount(subtotal, tax, total){
        if (window.location.pathname == '/cart/'){        
            $('#subtotal').html(subtotal)
            $('#tax').html(tax)
            $('#total').html(total)}
    }
});