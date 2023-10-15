function trim_name(input, max_length=16) {
    input.value = input.value.replace(/[^A-Za-z ]/g, '').replace(/ +/g, ' ').toLowerCase().split(' ').map(function(word) {
        return word.charAt(0).toUpperCase() + word.slice(1)
    }).join(' ').slice(0, max_length)
}

function trim_number(input, max_length=16) {
    input.value = input.value.replace(/[^\d]/g, '').slice(0, max_length)
}

function check_email(input) {
    if (!/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/.test(input.value))
        input.value = ''
}

function trim_usage(usage) {
    const kb = 2 ** 10
    const mb = kb * kb
    const gb = mb * kb

    if (usage < mb)
        return parseFloat((usage / kb).toFixed(2)) + 'KB'
    if (usage < gb)
        return parseFloat((usage / mb).toFixed(2)) + 'MB'
    return parseFloat((usage / gb).toFixed(2)) + 'GB'
}

function trim_countdown(countdown) {
    const second = 1000
    const minute = second * 60
    const hour = minute * 60
    const day = hour * 24

    if (countdown < minute)
        return Math.ceil(countdown / second) + ' Seconds'
    if (countdown < hour)
        return Math.ceil(countdown / minute) + ' Minutes'
    if (countdown < day)
        return Math.ceil(countdown / hour) + ' Hours'
    return Math.ceil(countdown / day) + ' Days'
}

function setFormMessage(form, type, message) {
    const element = form.querySelector('#message-box')

    element.classList.remove('form-success', 'form-error', 'form-warning')
    if (type == 'error' || type == 'success' || type == 'warning')
        element.classList.add(`form-${type}`)
    element.textContent = message
}

document.addEventListener('DOMContentLoaded', () => {
    let user_data = {}
    let user_type = ''
    let user_order = null
    let user_clients = []

    const mainContainer = document.querySelector('#main-container')
    const formContainer = document.querySelector('#form-container')
    const login = formContainer.querySelector('#login')
    const signup = formContainer.querySelector('#signup')
    const renew = formContainer.querySelector('#renew')
    const dataContainer = document.querySelector('#data-container')
    const article = dataContainer.querySelector('#request-article')
    const contentTable = dataContainer.querySelector('.content-table')
    const infinite = dataContainer.querySelector('#infinite-article')

    function showDataContainer() {
        let hideButton = true
        const current_datetime = new Date()

        dataContainer.hidden = false
        mainContainer.hidden = formContainer.hidden = infinite.hidden = true

        if (user_type == 'registered') {
            contentTable.hidden = false

            if (user_order) {
                article.hidden = false
                article.querySelector('#contact').hidden = true

                article.querySelector('#name').textContent = user_order.name.split(' - ')[0]
                article.querySelector('#plan').textContent = user_order.plan
                article.querySelector('#code').textContent = user_order.payment_code
                article.querySelector('#mobile').textContent = user_order.mobile
                article.querySelector('#email').textContent = user_order.email
            }
            else
                article.hidden = true

            contentTable.querySelector('#name').textContent = user_data.remark
            contentTable.querySelector('#usage').textContent = `${trim_usage(user_data.up)} / ${trim_usage(user_data.down)}`

            const status = contentTable.querySelector('#status')
            if (user_data.enable) {
                status.textContent = 'Active'
                status.classList.add('form-success')
                status.classList.remove('form-error', 'form-warning')
            }
            else {
                status.textContent = 'Inactive'
                status.classList.add('form-error')
                status.classList.remove('form-success', 'form-warning')
            }

            const remain = contentTable.querySelector('#remain')
            if (user_data.total == 0) {
                infinite.hidden = false
                remain.textContent = 'Infinite'
                remain.classList.add('form-success')
                remain.classList.remove('form-warning', 'form-error')
            }
            else {
                remain.textContent = `${trim_usage(Math.max(user_data.total - user_data.up - user_data.down, 0))}`
                remain.classList.remove('form-success', 'form-warning', 'form-error')
                hideButton = false

                if (!remain.textContent.endsWith('GB'))
                    remain.classList.add('form-error')
                else if (parseFloat(remain.textContent.slice(0, -2)) < 5)
                    remain.classList.add('form-warning')
                else
                    hideButton = true
            }

            const left = contentTable.querySelector('#left')
            if (user_data.expiry_time == 0) {
                left.textContent = 'Infinite'
                left.classList.add('form-success')
                left.classList.remove('form-warning', 'form-error')
            }
            else {
                const diff = Math.max(user_data.expiry_time - Date.now(), 0)
                left.classList.remove('form-success', 'form-warning', 'form-error')
                left.textContent = trim_countdown(diff)
                hideButton = false
                
                if (diff < 3 * 24 * 60 * 60 * 1000)
                    left.classList.add('form-error')
                else if (diff < 7 * 24 * 60 * 60 * 1000)
                    left.classList.add('form-warning')
                else
                    hideButton = true
            }

            const table = contentTable.querySelector('#clients')
            table.innerHTML = ''

            user_clients.forEach(client => {
                const row = table.insertRow()
                row.onmouseover = function() {
                    this.classList.add('active-row')
                }
                row.onmouseout = function() {
                    this.classList.remove('active-row')
                }

                row.insertCell().innerHTML = client.name.split(' (')[0]

                const status = row.insertCell()
                if (client.enable) {
                    status.textContent = 'Active'
                    status.classList.add('form-success')
                }
                else {
                    status.textContent = 'Inactive'
                    status.classList.add('form-error')
                }

                const left = row.insertCell()
                if (client.expiry_time == 0) {
                    left.textContent = 'Infinite'
                    left.classList.add('form-success')
                }
                else {
                    const diff = Math.max(client.expiry_time - Date.now(), 0)
                    left.textContent = trim_countdown(diff)
                    if (diff < 3 * 24 * 60 * 60 * 1000)
                        left.classList.add('form-error')
                    else if (diff < 7 * 24 * 60 * 60 * 1000)
                        left.classList.add('form-warning')
                }

                row.insertCell().textContent = `${trim_usage(client.up)} / ${trim_usage(client.down)}`
    
                const remain = row.insertCell()
                if (client.total == 0) {
                    remain.textContent = 'Infinite'
                    remain.classList.add('form-success')
                }
                else {
                    remain.textContent = `${trim_usage(Math.max(client.total - client.up - client.down, 0))}`
                    if (!remain.textContent.endsWith('GB'))
                        remain.classList.add('form-error')
                    else if (parseFloat(remain.textContent.slice(0, -2)) < 5)
                        remain.classList.add('form-warning')
                }
            })
        }
        else {
            contentTable.hidden = true
            article.hidden = article.querySelector('#contact').hidden = false

            article.querySelector('#name').textContent = user_data.name.split(' - ')[0]
            article.querySelector('#plan').textContent = user_data.plan
            article.querySelector('#code').textContent = user_data.payment_code
            article.querySelector('#mobile').textContent = user_data.mobile
            article.querySelector('#email').textContent = user_data.email
        }

        dataContainer.querySelector('#renew').hidden = hideButton | !article.hidden
        dataContainer.querySelector('#time').textContent = current_datetime.toLocaleString()
    }

    mainContainer.querySelector('#continue').addEventListener('click', () => {
        mainContainer.hidden = signup.hidden = renew.hidden = true
        formContainer.hidden = false
    })

    formContainer.querySelector('#goto-signup').addEventListener('click', event => {
        event.preventDefault()

        signup.hidden = false
        login.hidden = renew.hidden = true
        setFormMessage(signup, '', '')
    })
    formContainer.querySelector('#goto-login').addEventListener('click', event => {
        event.preventDefault()

        login.hidden = false
        signup.hidden = renew.hidden = true
        setFormMessage(login, '', '')
    })
    formContainer.querySelector('#goto-data').addEventListener('click', event => {
        event.preventDefault()

        mainContainer.hidden = formContainer.hidden = article.hidden = true
        dataContainer.hidden = contentTable.hidden = false
    })

    login.addEventListener('submit', event => {
        event.preventDefault()
        
        $.ajax({
            url: '/api/customer-data',
            type: 'POST',
            data: {
                firstname: login.querySelector('#firstname').value.trim(),
                lastname: login.querySelector('#lastname').value.trim()
            },
            headers: {
                'X-CSRFToken': csrf_token
            },
            success: data => {
                console.log(data)
                user_data = data.data
                user_order = data.order
                user_type = data.user_type
                user_clients = data.clients
                setFormMessage(login, 'success', "You're in! You have successfully logged in.")
                showDataContainer()
            },
            error: (xhr, status, error) => {
                console.log('Error:', xhr.responseJSON.message)
                setFormMessage(login, 'error', "Sorry, we couldn't find a user with that name. Please check your spelling and try again.")
            }
        })
    })
    signup.addEventListener('submit', event => {
        event.preventDefault()

        const form_data = {
            firstname: signup.querySelector('#firstname').value.trim(),
            lastname: signup.querySelector('#lastname').value.trim(),
            destination_card: signup.querySelector('#card').value,
            payment_code: signup.querySelector('#code').value,
            mobile: signup.querySelector('#mobile').value,
            email: signup.querySelector('#email').value,
            plan: signup.querySelector('#plan').value
        }

        $.ajax({
            url: '/api/add-customer',
            type: 'POST',
            data: form_data,
            headers: {
                'X-CSRFToken': csrf_token
            },
            success: data => {
                console.log(data)
                if (form_data.payment_code == '') {
                    window.location.replace(`https://www.zarinpal.com/pg/StartPay/${data.authority}`)
                    return
                }

                user_data = {
                    name: `${form_data.firstname} - ${form_data.lastname}`,
                    destination_card: form_data.destination_card,
                    payment_code: form_data.payment_code,
                    mobile: form_data.mobile,
                    email: form_data.email,
                    plan: form_data.plan
                }
                user_order = null
                user_type = 'waitlist'
                setFormMessage(signup, 'success', 'Hooray! You have successfully joined us.')
                showDataContainer()
            },
            error: (xhr, status, error) => {
                console.log('Error:', xhr.responseJSON.message)
                if (xhr.status == 403)
                    setFormMessage(signup, 'warning', "We're sorry, but our server is currently at full capacity and we are unable to process new registrations at this time. Please try again later or contact our support team for further assistance.")
                else
                    setFormMessage(signup, 'error', 'The name you entered is already in use, or the payment code provided has already been redeemed. Please choose a different name, check your payment code, or contact our support team if you have any questions.')
            }
        })
    })
    renew.addEventListener('submit', event => {
        event.preventDefault()

        const form_data = {
            firstname: renew.querySelector('#firstname').value,
            lastname: renew.querySelector('#lastname').value,
            destination_card: renew.querySelector('#card').value,
            payment_code: renew.querySelector('#code').value,
            plan: renew.querySelector('#plan').value
        }

        $.ajax({
            url: '/api/add-customer',
            type: 'POST',
            data: form_data,
            headers: {
                'X-CSRFToken': csrf_token
            },
            success: data => {
                console.log(data)
                if (form_data.payment_code == '') {
                    window.location.replace(`https://www.zarinpal.com/pg/StartPay/${data.authority}`)
                    return
                }

                user_order = {
                    'name': `${form_data.firstname} - ${form_data.lastname}`,
                    'destination_card': form_data.destination_card,
                    'mobile': 'provided during registration',
                    'email': 'provided during registration',
                    'payment_code': form_data.payment_code,
                    'plan': form_data.plan
                }
                setFormMessage(renew, 'success', 'Your account renewal request has been received and recorded.')
                showDataContainer()
            },
            error: (xhr, status, error) => {
                console.log('Error:', xhr.responseJSON.message)
                setFormMessage(renew, 'error', 'Sorry, an error occurred while processing your account renewal request.')
            }
        })
    })

    dataContainer.querySelector('#renew').addEventListener('click', event => {
        event.preventDefault()

        formContainer.hidden = renew.hidden = false
        mainContainer.hidden = dataContainer.hidden = login.hidden = signup.hidden = true

        renew.querySelector('#firstname').value = user_data.remark.split(' - ')[0]
        renew.querySelector('#lastname').value = user_data.remark.split(' - ')[1]
    })
    dataContainer.querySelector('#logout').addEventListener('click', event => {
        event.preventDefault()
        
        user_data = {}
        formContainer.hidden = login.hidden = false
        mainContainer.hidden = dataContainer.hidden = signup.hidden = renew.hidden = true
        setFormMessage(login, 'success', 'Logout successful. Thank you for using our service. Have a great day!')
    })
    dataContainer.querySelector('#update').addEventListener('click', event => {
        event.preventDefault()

        const name = user_type == 'registered'? user_data.remark: user_data.name
        $.ajax({
            url: '/api/customer-data',
            type: 'POST',
            data: {
                firstname: name.split(' - ')[0],
                lastname: name.split(' - ')[1]
            },
            headers: {
                'X-CSRFToken': csrf_token
            },
            success: data => {
                console.log(data)
                user_data = data.data
                user_order = data.order
                user_type = data.user_type
                showDataContainer()
            },
            error: (xhr, status, error) => {
                console.log('Error:', xhr.responseJSON.message)
            }
        })
    })

    signup.querySelector('#card').addEventListener('change', event => {
        event.preventDefault()

        const code = signup.querySelector('#code')
        if (signup.querySelector('#card').value == 'ZarinPal') {
            code.value = ''
            code.type = 'hidden'
            code.required = false
        }
        else {
            code.type = 'text'
            code.required = true
        }
    })
    renew.querySelector('#card').addEventListener('change', event => {
        event.preventDefault()

        const code = renew.querySelector('#code')
        if (renew.querySelector('#card').value == 'ZarinPal') {
            code.value = ''
            code.type = 'hidden'
            code.required = false
        }
        else {
            code.type = 'text'
            code.required = true
        }
    })
})