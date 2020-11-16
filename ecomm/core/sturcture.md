1 Item
    title 
    image 
    price
    discription 
    slug
    choice 
    label

2 OrderItem
    user
    item (Item)
    ordered = False

3 Order

    user 
    OrderItem (Many To Many filed)
    order_date (date)
    ordered_date (date and time)
    ordered False




