
// function initShippingOption(
//   prefix,
//   shippingCountrySelectId='id_shipping-country',
//   shippingOptionSelectId='id_shipping_option') {
//     var select = $('#' + shippingOptionSelectId);
//     var countrySelect = $('#'+shippingCountrySelectId);
//     // countrySelect.removeEventListener('change');
//     // countrySelect.off('change');
//     // countrySelect.change(function(e) {
//     countrySelect.addEventListener('change', function(e) {
//       select.find('option').remove();
//       longclawclient.shippingCountryOptions.get({
//         prefix,
//         urlParams: {
//           country: countrySelect.val()
//         }
//       }).then((data) => {
//           for (let i = 0; i < data.length; ++i) {
//             var shippingRate = data[i];
//             select.append($('<option />', {value: shippingRate.name, text: shippingRate.name}));
//           }
//       });
//     });
// }


function initShippingOption(
  prefix,
  shippingCountrySelectId='id_shipping-country',
  shippingOptionSelectId='id_shipping_option') {
    console.log('HELLO?');
    var select = document.getElementById(shippingOptionSelectId);
    var countrySelect = document.getElementById(shippingCountrySelectId);

    countrySelect.addEventListener('change', function(e) {
      console.log('country select changed');

      // remove all the shipping select options
      var shippingOptions = select.querySelectorAll('option');
      for (var i = 0; i < shippingOptions.length; i++) {
        shippingOptions[i].parentNode.removeChild(shippingOptions[i]);
      }

      // get the new shipping select options based on the country
      longclawclient.shippingCountryOptions.get({
        prefix,
        urlParams: {
          country: countrySelect.value
        }
      }).then((data) => {
        console.log('got some farken data back');
        console.log(data);
        for (var i = 0; i < data.length; i++) {
          var shippingRate = data[i];
          var selectChild = document.createElement('option');
          selectChild.value = shippingRate.name;
          selectChild.innerHTML = shippingRate.name;
          select.appendChild(selectChild);
        }
      });
    });
}