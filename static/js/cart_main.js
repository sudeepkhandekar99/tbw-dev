// console.log("Hello world!");
// console.log("User: " , user);

// var updateBtns = document.getElementsByClassName('update-cart')

// for (i = 0; i < updateBtns.length; i++) {
// 	updateBtns[i].addEventListener('click', function(){
// 		var productId = this.dataset.product
// 		var action = this.dataset.action
// 		console.log('productId:', productId, 'Action:', action)
// 		console.log('USER:', user)

// 		if (user == 'AnonymousUser'){
// 			addCookieItem(productId, action)
// 		}else{
// 			updateUserOrder(productId, action)
// 		}
// 	})
// }

function updateUserOrder(productId, action) {
    console.log("Item added.")
}

var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
        var size_ = this.dataset.size
        var color = this.dataset.finalcolor
		console.log('productId:', productId, 'Action:', action)
		console.log('USER:', user)

		if (user == 'AnonymousUser'){
			console.log("Login first! -.-")
		}else{
			updateUserOrder(productId, action, size_, color)
		}
	})
}

function updateUserOrder(productId, action, size_, color) {
    var url = "/update_item"
    fetch(url, {
        method : "POST",
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken' : csrftoken
        },
        body : JSON.stringify({'productId': productId, 'action': action, 'size' : size_, 'color' : color})
    })
    .then((response) => {
        return response.json()
    })
    .then((data) => {
        // console.log('data', data)
        location.reload()
    })
}