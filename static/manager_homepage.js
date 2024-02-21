const parent = new Vue({
    el: '#app',
    data: {
      selected: '',
      categories: [],
      items: [],
      category_selected: "Select a Category",
      old_item_name: "", //used for editing item
    },
    methods: {
        add_store() {
            this.selected="add_store"
        },
        add_category() {
          this.selected="add_category"
        },
        add_new_item() {
            this.selected="add_new_item"
        },
        add_item() {
            this.selected="add_item"
        },
        edit_category(){
          this.selected="edit_category"
        },
        edit_item(){
          this.selected="edit_item"
        },
        edit_store(){
          this.selected="edit_store"
        },
        async getData() {
          const [res1, res2] = await Promise.all([
            await fetch('http://127.0.0.1:8080/api/categories'),
            await fetch('http://127.0.0.1:8080/api/items'),
          ]);
          try{
            const categories_ = await res1.json()
            this.categories = categories_
          }catch{}              
          try{
            const items_ = await res2.json()
            this.items= items_
          }catch{}
        }
    },
    computed: {
      items_to_select: function(){
        temp = []
        for (i=0; i<this.items.length; i++){
          if (this.items[i].category_name==this.category_selected){
            temp.push(this.items[i].name)
          }
        }
        return temp;
      },
      edit_unit: function(){
        for (i=0; i<this.items.length; i++){
          if (this.items[i].name==this.old_item_name){
            return this.items[i].unit
          }
        }
        return ""
      },
      edit_price: function(){
        for (i=0; i<this.items.length; i++){
          if (this.items[i].name==this.old_item_name){
            return this.items[i].price
          }
        }
        return ""
      },
      edit_best_before: function(){
        for (i=0; i<this.items.length; i++){
          if (this.items[i].name==this.old_item_name){
            return this.items[i].best_before
          }
        }
        return ""
      },
    },
    mounted() {
      this.getData()
    },       
    delimiters : ['[[', ']]']
  })