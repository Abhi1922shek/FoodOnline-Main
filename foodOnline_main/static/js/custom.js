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