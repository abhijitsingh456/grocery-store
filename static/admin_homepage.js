const parent = new Vue({
  el: '#app',  
  data: {
        stores_waiting: [],
        categories_waiting: [],
        items_waiting: [],
        del_categories_waiting: [],
        del_items_waiting: []
  },
  methods: {
    async getData() {
      /*
      const res = await fetch('http://127.0.0.1:8080/api/stores_waiting')
      const stores_waiting_ = await res.json()
      this.stores_waiting = stores_waiting_

      res = await fetch('http://127.0.0.1:8080/api/items_waiting')
      const items_waiting_ = await res.json()
      this.items_waiting = items_waiting_

      res = await fetch('http://127.0.0.1:8080/api/categories_waiting')
      const categories_waiting_ = await res.json()
      this.categories_waiting = categories_waiting_
      */

      const [res1, res2, res3, res4, res5] = await Promise.all([
        await fetch('http://127.0.0.1:8080/api/stores_waiting'),
        await fetch('http://127.0.0.1:8080/api/items_waiting'),
        await fetch('http://127.0.0.1:8080/api/categories_waiting'),
        await fetch('http://127.0.0.1:8080/api/del_categories_waiting'),
        await fetch('http://127.0.0.1:8080/api/del_items_waiting')
      ]);
      try{
        const items_waiting_ = await res2.json()
        this.items_waiting = items_waiting_
      }catch{}
      try{
        const categories_waiting_ = await res3.json()
        this.categories_waiting = categories_waiting_
      }catch{}
      try{
        const stores_waiting_ = await res1.json()
        this.stores_waiting = stores_waiting_  
      }catch{}
      try{
        const del_categories_waiting_ = await res4.json()
        this.del_categories_waiting = del_categories_waiting_  
      }catch{}
      try{
        const del_items_waiting_ = await res5.json()
        this.del_items_waiting = del_items_waiting_  
      }catch{}               
    },  
  },
  beforeMount() {
    this.getData()
  },
  delimiters : ['[[', ']]']
})