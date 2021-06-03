/*----- MENU -----*/
const showMenu = (toggleId,navId) =>{
    const toggle = document.getElementById(toggleId),
    nav = document.getElementById(navId)

    if(toggle && nav){
        toggle.addEventListener('click', ()=>{
            nav.classList.toggle('show')
        })
    }
}
showMenu('nav-toggle','nav-menu')

/*----- CAMBIO COLORS -----*/
const sizes = document.querySelectorAll('.size__tallas');
const colors = document.querySelectorAll('.sneaker__color');
const sneaker = document.querySelectorAll('.sneaker__img');

function changeSize(){
    sizes.forEach(size => size.classList.remove('active'));
    this.classList.add('active');
}

function changeColor(){
    let primary = this.getAttribute('primary');
    let color = this.getAttribute('color');
    let sneakerColor = document.querySelector(`.sneaker__img[color="${color}"]`);

    colors.forEach(c => c.classList.remove('active'));
    this.classList.add('active');

    document.documentElement.style.setProperty('--primary', primary);

    sneaker.forEach(s => s.classList.remove('shows'));
    sneakerColor.classList.add('shows')
}

sizes.forEach(size => size.addEventListener('click', changeSize));
colors.forEach(c => c.addEventListener('click', changeColor));

/* ====== UPDATE CART/ADD ITEM =========== */
var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
        var sizes = ['radio_xs', 'radio_s','radio_m', 'radio_l', 'radio_xl', 'radio_c']
        var size_ = "M"
        sizes.forEach(item=>{
            if(document.getElementById(item).checked) {
                size_ = document.getElementById(item).value
            }
        })

        var colors = [
            'radio_yellow', 
            'radio_turquoise', 
            'radio_red', 
            'radio_black', 
            'radio_blue', 
            'radio_light-pink',
            'radio_rosegold',
            'radio_pistachio-green',
            'radio_navy-blue',
            'radio_bottle-green',
            'radio_hot-pink',
            'radio_dusty-pink',
            'radio_baby-pink',
            'radio_beige',
            'radio_sea-green',
            'radio_lemon-yellow',
            'radio_mustard',
            'radio_maroon',
        ]
        var finalColor = colors[0]
        colors.forEach(color=>{
            let a = document.getElementById(color)
            if(a) {
                if(a.checked) {
                    finalColor = a.value
                }
            }
        })
		console.log('productId:', productId, 'Action:', action, 'size:' , size_, 'color', finalColor)
		console.log('USER:', user)

		if (user == 'AnonymousUser'){
            alert("Login first!")
			// console.log("Login first! -.-")
		}else{
			updateUserOrder(productId, action, size_, finalColor)
		}
	})
}

function updateUserOrder(productId, action, size_, finalColor) {
    console.log("here")
    var url = "/update_item"
    fetch(url, {
        method : "POST",
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken' : csrftoken
        },
        body : JSON.stringify({'productId': productId, 'action': action, 'size' : size_, 'color': finalColor})
    })
    .then((response) => {
        return response.json()
    })
    .then((data) => {
        // console.log('data', data)
        location.reload()
    })
}