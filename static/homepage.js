const parent = new Vue({
  el: '#app',
  data: {
    categories: [],
    items: [],
    items_to_display: [],
    cart: [],
    store_name: "",
    quantity: "",
    flags: [], //will have length same as the highest item.id
    cart_flag: false,
    search_query: "",

    /*
    items_to_display = [{cat_name:"", items_in_cat: [{}, {}]}, 
                        {cat_name:"", items_in_cat: [{}, {}]}]
    */
    /*
    items_in_cat:[{
     "id":"",
     "name":"",
     .
     .
     stores:[{store_name:"",quantity_rem:""},{store_name:"",quantity_rem:""}]
    }]
    */
  },
  methods: {
    async getData() {
      const [res1, res2] = await Promise.all([
        await fetch('http://127.0.0.1:8080/api/categories'),
        await fetch('http://127.0.0.1:8080/api/items'),
      ]);
      try {
        const categories_ = await res1.json()
        this.categories = categories_
      } catch { }
      try {
        const items_ = await res2.json()
        this.items = items_
      } catch { }

      for (let i = 0; i < this.categories.length; i++) {
        let temp = {
          cat_name: this.categories[i].name,
          items_in_cat: []
        }
        this.items_to_display.push(temp)
      }
      let largest_item_id = 0;
      for (let i = 0; i < this.items.length; i++) {
        //finding the largest items.id to decide the size of flags variable
        if (this.items[i].id > largest_item_id) {
          largest_item_id = this.items[i].id
        }
        for (let j = 0; j < this.items_to_display.length; j++) {
          if (this.items_to_display[j].cat_name == this.items[i].category_name) {
            //make an API call to get all the stores selling this.items[i]
            let stores = await fetch('http://127.0.0.1:8080/api/stores/' + this.items[i].id)
            this.items[i].stores = await stores.json()
            this.items_to_display[j].items_in_cat.push(this.items[i])
          }
        }
      }
      this.flags = new Array(largest_item_id + 1).fill("0");
    },

    changeFlag(item_id) {
      if (this.flags[item_id] == "0") {
        Vue.set(this.flags, item_id, "1");
        this.item_name = "";
        this.store_name = "";
        this.quantity = 0;
        for (let i = 0; i < this.flags.length; i++) {
          if (i != item_id) {
            this.flags[i] = "0";
          }
        }
      } else {
        this.flags[item_id] = "0";
      }
    },
    add_to_cart(item_name, item_price, user_id) {
      if (this.store_name=="" || this.quantity==0){
        return;
      }
      order = {
        "user_id":user_id,
        "item_name": item_name,
        "store_name": this.store_name,
        "quantity": this.quantity,
        "total_amount": parseInt(item_price) * parseInt(this.quantity)
      }
      this.cart.push(order)
      this.item_name = "";
      this.store_name = "";
      this.quantity = 0;
    },

    change_cart_flag() {
      this.cart_flag = !this.cart_flag
    },

    async checkout() {
      await fetch("http://127.0.0.1:8080/checkout", {

        // Adding method type
        method: "POST",

        // Adding body or contents to send
        body: JSON.stringify(this.cart),

        // Adding headers to the request
        headers: {
          "Content-type": "application/json; charset=UTF-8"
        }
      }),
      this.cart = []
    }
  },
  computed: {
    total_order_amount: function () {
      let sum = 0;
      for (let i = 0; i < this.cart.length; i++) {
        sum += this.cart[i].total_amount
      }
      return sum
    },
    search_results: function(){
      search_results_list = [];
      for (let i=0; i<this.items_to_display.length; i++){
        if (this.items_to_display[i].cat_name.toLowerCase().includes(this.search_query.toLowerCase())){
          search_results_list.push(this.items_to_display[i])
        }
        else{
          temp = [];
          for (let j=0; j<this.items_to_display[i].items_in_cat.length; j++){
            if (this.items_to_display[i].items_in_cat[j].name.toLowerCase().includes(this.search_query.toLowerCase())){
              temp.push(this.items_to_display[i].items_in_cat[j])
            }
          }
          if (temp.length != 0){
          obj = {"cat_name":this.items_to_display[i].cat_name,"items_in_cat":temp}
          search_results_list.push(obj)
          }
        }
      }
      return search_results_list;
    }
  },
  mounted() {
    this.getData()
  },
  delimiters: ['[[', ']]']
})

    /*
    items_to_display = [{cat_name:"", items_in_cat: [{}, {}]}, 
                        {cat_name:"", items_in_cat: [{}, {}]}]
    */
    /*
    items_in_cat:[{
     "id":"",
     "name":"",
     .
     .
     stores:[{store_name:"",quantity_rem:""},{store_name:"",quantity_rem:""}]
    }]
    */