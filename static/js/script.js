function initializeCartFunctionality() {
    
    document.body.addEventListener('click', (e) => {
        
        let updateCartElement = e.target.closest('.update-cart');
        if (updateCartElement) {
            e.preventDefault(); // Prevent any default action
            e.stopPropagation(); // Stop event from bubbling up
            
            let productSlug = updateCartElement.getAttribute('data-product-slug');
            let action = updateCartElement.getAttribute('data-action');
            let quantity = updateCartElement.getAttribute('data-quantity');

            if (typeof user === 'undefined' || user === 'AnonymousUser') {
                updateCartCookie(productSlug, action, quantity);
            } else {
                updateCart(productSlug, action, quantity);
            }
        } 
    });
}

document.addEventListener('DOMContentLoaded', initializeCartFunctionality);

updateCart = (productSlug, action, quantity) => {
	let url = "/api/update_item/"
	fetch(url, {
		method: 'POST',
		headers:{
			'Content-Type':'application/json',
			'X-CSRFToken': CSRF_TOKEN
		},
		body: JSON.stringify({
			'product_slug': productSlug,
			'action': action,
			'quantity': quantity})
	})
	.then((response) => {
		if (!response.ok) {
			throw new Error(`HTTP error status: ${response.status}`);
		}
		return response.json()
	})
	.then((data) => {
		if(data.success === true) {
			if(action === 'add_then_checkout') {
					window.location.href = '/checkout/'
			}
			
			if(action === 'add') {
					showPopup('thêm vào giỏ hàng');
			} else if(action === 'remove') {
					showPopup('ra khỏi giỏ hàng');
			}
			document.getElementById('cart-total').innerHTML = data.total_quantity

			if(window.location.pathname === '/cart/') {
					let quantityDisplay = document.getElementById(`cart-item-${productSlug}`)
					if(quantityDisplay) {
							quantityDisplay.textContent = data.item_quantity
					}

					const productPrice = document.getElementById(`product-price-${productSlug}`);
					if (productPrice) {
							productPrice.textContent = formatPrice(data.product_price) + 'đ';
					}

					// Update item total price
					const itemTotalPrice = document.getElementById(`item-total-price-${productSlug}`);
					if (itemTotalPrice) {
							itemTotalPrice.textContent = formatPrice(data.item_total_price) + 'đ';
					}

					let orderTotalPrice = document.getElementById('order-total-price');
					if (orderTotalPrice) {
					orderTotalPrice.textContent = formatPrice(data.order_total_price) + 'đ';
					}

					if (data.deleted_item_id !== -1) {
					const deletedItem = document.getElementById(`cart-item-${data.deleted_item_id}`);
							if (deletedItem) {
									deletedItem.remove();
							}
					}

			}
		}
	})
	.catch((error)=>{
		console.log('error here', error)
	})
}

function updateCartCookie(productSlug, action, quantity) {
    let intQuantity = parseInt(quantity);
    if (isNaN(intQuantity)) {
        console.error('Invalid quantity:', quantity);
        return;
    }

    if (typeof cart === 'undefined') {
        console.error('Cart is undefined');
        cart = {};
    }

    let cartTotal = 0;
    let cartQuantity = 0;

    if (action === 'add' || action === 'add_then_checkout') {
        if (cart[productSlug] === undefined) {
            cart[productSlug] = {'quantity': intQuantity};
        } else {
            cart[productSlug]['quantity'] += intQuantity;
        }

        if (action === 'add_then_checkout') {
            window.location.href = '/checkout/';
        }

        showPopup(intQuantity + ' vào giỏ');
    } else if (action === 'remove') {
        if (cart[productSlug]) {
            cart[productSlug]['quantity'] -= intQuantity;
            showPopup('ra giỏ');
        }
    } else if (action === 'remove_all') {
        if (cart[productSlug]) {
            cart[productSlug]['quantity'] = 0;
            showPopup('ra giỏ');
        }
    }

    // Remove items with zero quantity and calculate totals
    for (let slug in cart) {
        if (cart[slug]['quantity'] <= 0) {
            delete cart[slug];
			let itemRow = document.querySelector(`tr[id^="cart-item-"]:has([data-product-slug="${slug}"])`);
			if (itemRow) {
				itemRow.style.transition = 'all 0.3s ease-in-out';
                itemRow.style.maxHeight = `${itemRow.offsetHeight}px`;
                itemRow.style.opacity = '0';
                itemRow.style.overflow = 'hidden';
                setTimeout(() => {
                    itemRow.remove();
                }, 300);
			}
        } else {
            cartQuantity += cart[slug]['quantity'];
            
            
            let priceElement = document.getElementById(`product-price-${slug}`);
            let price = 0;
            if (priceElement) {
                price = deformatPrice(priceElement.textContent);
            }

            let itemTotal = cart[slug]['quantity'] * price;
            cartTotal += itemTotal;

            // Update item quantity display
            let quantityDisplay = document.getElementById(`cart-item-${slug}`);
            if (quantityDisplay) {
                quantityDisplay.textContent = cart[slug]['quantity'];
            }

            // Update item total price display
            let itemTotalPrice = document.getElementById(`item-total-price-${slug}`);
            if (itemTotalPrice) {
                itemTotalPrice.textContent = formatPrice(itemTotal) + 'đ';
            }
        }
    }

    // Update cart total quantity display
    let cartTotalElement = document.getElementById('cart-total');
    if (cartTotalElement) {
        cartTotalElement.innerHTML = cartQuantity;
    }

    // Update order total price display
    let orderTotalPrice = document.getElementById('order-total-price');
    if (orderTotalPrice) {
        orderTotalPrice.textContent = formatPrice(cartTotal) + 'đ';
    }

    document.cookie = 'cart=' + JSON.stringify(cart) + ';domain=;path=/;SameSite=Lax';
}


function deformatPrice(priceString) {
    return parseInt(priceString.replace(/[^\d]/g, ''));
}

function formatPrice(price) {
	return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

let activePopups = [];
let popupCount = 0;

function showPopup(message) {
		const popup = document.createElement('div');
		popup.textContent = message;
		popup.style.cssText = `
				position: fixed;
				top: 20px;
				right: 20px;
				background-color: #4CAF50;
				color: white;
				padding: 15px;
				border-radius: 5px;
				z-index: 1000;
				opacity: 0;
				transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
				transform: translateY(-20px);
		`;

		// Assign a unique ID to each popup
		const popupId = `popup-${popupCount++}`;
		popup.id = popupId;

		// Adjust positions of existing popups
		activePopups.forEach((existingPopup, index) => {
				existingPopup.style.transform = `translateY(${(index + 1) * 70}px)`;
		});

		// Add new popup to the array and DOM
		activePopups.unshift(popup);
		document.body.appendChild(popup);

		// Fade in
		setTimeout(() => {
				popup.style.opacity = '1';
				popup.style.transform = 'translateY(0)';
		}, 10);

		// Remove after 2 seconds
		setTimeout(() => {
				removePopup(popupId);
		}, 2000);
}

function removePopup(popupId) {
		const index = activePopups.findIndex(popup => popup.id === popupId);
		if (index > -1) {
				const popup = activePopups[index];
				popup.style.opacity = '0';
				popup.style.transform = 'translateY(-20px)';
				
				setTimeout(() => {
						document.body.removeChild(popup);
						activePopups.splice(index, 1);
						
						// Adjust positions of remaining popups
						activePopups.forEach((remainingPopup, i) => {
								remainingPopup.style.transform = `translateY(${i * 70}px)`;
						});
				}, 300);
		}
}

// Get the button:
let mybutton = document.getElementById("myBtn");

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function () {
	scrollFunction();
};

function scrollFunction() {
	if (
		document.body.scrollTop > 20 ||
		document.documentElement.scrollTop > 20
	) {
		mybutton.style.display = "block";
	} else {
		mybutton.style.display = "none";
	}
}

function topFunction() {
	document.body.scrollTop = 0; // For Safari
	document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

const prevIcon = '<i class="fa fa-angle-left fa-2x"></i>';
const prevArrow = '<button class="slick-next slick-arrow" aria-label="Next" type="button" style="display: block;"><i class="fa fa-angle-right fa-2x"></i></button>'
const nextIcon = '<i class="fa fa-angle-right fa-2x"></i>';
const nextArrow = '<button class="slick-prev slick-arrow" aria-label="Previous" type="button" style="display: block;"><i class="fa fa-angle-left fa-2x"></i></button>'

$(document).ready(function() {
	// Main slider
	$('.main-slider').slick({
		slidesToShow: 1,
		slidesToScroll: 1,
		arrows: false,
		fade: true,
		asNavFor: '.nav-slider'
	});

	// Nav slider
	$('.nav-slider').slick({
		slidesToShow: 3,
		slidesToScroll: 1,
		asNavFor: '.main-slider',
		centerMode: true,
		focusOnSelect: true,
		prevArrow: prevArrow,
		nextArrow: nextArrow
	});
});

document.addEventListener('DOMContentLoaded', function() {
	setTimeout(function() {
			var messages = document.querySelectorAll('.messages li');
			messages.forEach(function(message) {
					var fadeOut = setInterval(function() {
							if (!message.style.opacity) {
									message.style.opacity = 1;
							}
							if (message.style.opacity > 0) {
									message.style.opacity -= 0.1;
							} else {
									clearInterval(fadeOut);
									message.style.display = 'none';
							}
					}, 200); 
			});
	}, 4000); 
});