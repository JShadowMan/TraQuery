'use strict';

// Header Component: load-bar
Vue.component('load-bar', {
    template: '<transition name="fade"><div class="load-bar" :class="class_object" v-if="show_load_bar" :style="style_object"></div></transition>',
    props: {
        'progress': {
            type: Number,
            default: 0
        }
    },
    computed: {
        show_load_bar: function() {
            return (this.progress > 0 && this.progress < 100);
        },
        style_object: function() {
            return {
                width: this.progress + '%'
            }
        },
        class_object: function() {
            return {
                'is-loading': this.show_load_bar
            }
        }
    }
});

// Header Component: Introduce
Vue.component('toolkit-intro', {
    template: '<article id="introduce">\
                <h1>Train Query Helper</h1>\
                <p>Distributed under the MIT License.<br/>Implemented in Python. Written by ShadowMan(Wang).</p>\
                <p class="server-status">\
                    <span>Online: <span :style="online_style">{{ online_count }}</span></span>\
                    <span>Active: <span :style="active_style">{{ active_count }}</span></span>\
                </p>\
               </article>',
    props: [ 'online_count', 'active_count' ],
    computed: {
        online_style: function() {
            return {
                color: this.online_count < 10 ? 'green' : 'red'
            }
        },
        active_style: function() {
            return {
                color: this.active_count < 5 ? 'green' : 'red'
            }
        }
    }
});

// Header Component
Vue.component('train-query-header', {
    template: '<header>' +
                  '<load-bar :progress="progress"></load-bar>' +
                  '<toolkit-intro :online_count="online_count" :active_count="active_count"></toolkit-intro>' +
              '</header>',
    props: [ 'progress', 'online_count', 'active_count' ]
});

// Body Component
Vue.component('input-group', {
    template: '<div>' +
                  '<label :for="name" :class="labelClass">{{ label }}</label>' +
                  '<input v-if="type == \'text\'" :class="inputClass" type="text" :name="name" :id="name" v-model="input_value" @change="send_value">' +
                  '<input v-if="type == \'date\'" :class="inputClass" type="date" :name="name" :id="name" v-model="input_value" @change="send_value">' +
              '</div>',
    props: [ 'label', 'name', 'label-class', 'input-class', 'type' ],
    data: function() {
        return {
            input_value: ''
        }
    },
    methods: {
        send_value: function() {
            this.$emit('receive_data', {
                name: this.name,
                value: this.input_value
            })
        }
    }
});

Vue.component('train-query-result-item', {

});

Vue.component('train-query-parameter', {
    template: '<section class="train-query-parameter"><form>' +
                  '<input-group type="text" label="FROM" name="from_station" label-class="input-group-label" input-class="input-group-input" @receive_data="receive_data"></input-group>' +
                  '<input-group type="text" label="TO" name="to_station" label-class="input-group-label" input-class="input-group-input" @receive_data="receive_data"></input-group>' +
                  '<input-group type="date" label="DATE" name="train_date" label-class="input-group-label" input-class="input-group-input" @receive_data="receive_data"></input-group>' +
                  '<button class="train-query-submit">Submit</button>' +
              '</form></section>',
    data: function() {
        return {
            from_station: '',
            to_station: '',
            train_date: ''
        }
    },
    methods: {
        receive_data: function(data) {
            switch (data.name) {
                case 'from_station': this.from_station = data.value; break;
                case 'to_station': this.to_station = data.value; break;
                case 'train_date': this.train_date = data.value; break;
            }
        }
    }
});

Vue.component('train-query-contents', {
    template: '<section class="container">\
                   <train-query-parameter></train-query-parameter>\
               </section>'
});

Vue.component('train-query-footer', {
    template: '<footer></footer>'
});