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

// Body Component: input-group
Vue.component('input-group', {
    template: '<div>' +
                  '<label :for="name" :class="labelClass">{{ label }}</label>' +
                  '<input v-if="type == \'text\'" :class="inputClass" type="text" :style="input_style" :name="name" v-model="input_value" @change="send_input_value">' +
                  '<input v-if="type == \'date\'" :class="inputClass" type="date" :style="input_style" :name="name" v-model="input_value" @change="send_input_value">' +
              '</div>',
    props: [ 'label', 'name', 'label-class', 'input-class', 'type' ],
    data: function() {
        return {
            input_value: '',
            input_status: 'default'
        }
    },
    computed: {
        input_style: function() {
            if (!this.input_value.length) {
                this.input_status = 'default';
                return { borderColor: null };
            }

            switch (this.input_status) {
                case 'default': break;
                case 'error': return { borderColor: '#F00' }; break;
                case 'success': return { borderColor: '#0F0' }; break;
                case 'waiting': return { borderColor: '#FF0' }; break;
            }
        }
    },
    methods: {
        send_input_value: function() {
            this.$emit('receive_input_data', {
                name: this.name,
                value: this.input_value
            })
        }
    }
});

Vue.component('train-query-parameter', {
    template: '<section class="train-query-parameter"><form>' +
                  '<input-group type="text" label="FROM" name="from_station" ref="from_station" label-class="input-group-label" input-class="input-group-input" @receive_input_data="parse_input_data"></input-group>' +
                  '<input-group type="text" label="TO" name="to_station" ref="to_station" label-class="input-group-label" input-class="input-group-input" @receive_input_data="parse_input_data"></input-group>' +
                  '<input-group type="date" label="DATE" name="train_date" ref="train_date" label-class="input-group-label" input-class="input-group-input" @receive_input_data="parse_input_data"></input-group>' +
                  '<button class="train-query-submit widget-btn widget-btn-default" :class="button_style" :disabled="is_disable">Start</button>' +
              '</form></section>',
    props: [ 'from-station', 'to-station', 'train-date' ],
    computed: {
        button_style: function() {
            var button_style_name = null;
            if (this.fromStation && this.toStation && this.trainDate) {
                button_style_name = 'default';
            } else {
                button_style_name = 'disabled';
            }

            return 'widget-btn-' + button_style_name;
        },
        is_disable: function() {
            return this.button_style == 'widget-btn-disabled';
        }
    },
    methods: {
        parse_input_data: function(data) {
            // is station data
            if (data.name === 'from_station' || data.name === 'to_station') {
                // the value is empty, notice parent-component, break
                if (!data.value.length) {
                    this.$emit('receive_input_true_data', data.name, '');
                    return;
                }
                // send request, check station exists
                this.$root.socket.emit('request.train.station', { station_name: data.value, key: data.name });

                // Vue instance reference
                var _self = this;
                // socket.io event
                this.$root.socket.on('response.train.station', function(response) {
                    // input-group component reference
                    var sub_component = (response.key === 'from_station') ? _self.$refs.from_station : _self.$refs.to_station;
                    // the station is exists
                    if (response.status === true) {
                        // update sub-component status
                        sub_component.input_status = 'success';
                        // emit parent-component event
                        this.$emit('receive_input_true_data', response.key, response.station_code);
                    // station non-exists
                    } else {
                        // update sub-component status
                        sub_component.input_status = 'error';

                        // show error message
                        console.log(response.message);
                    }
                }.bind(this));
            // is date data
            } else if (data.name === 'train_date') {
                var sub_component = this.$refs.train_date;
                var select_date = new Date(data.value.replace(/-/g, '/'));
                var current_date = new Date();

                var select_date_timestamp = select_date.getTime() / 1000;
                var current_date_timestamp = current_date.getTime() / 1000;

                if (current_date_timestamp - select_date_timestamp < 86400) {
                    sub_component.input_status = 'success';
                    this.$emit('receive_input_true_data', 'train_date', data.value);
                } else if (select_date_timestamp > current_date_timestamp) {
                    sub_component.input_status = 'success';
                    this.$emit('receive_input_true_data', data.name, data.value);
                } else {
                    this.$emit('receive_input_true_data', data.name, '');
                    sub_component.input_status = 'error';
                }
            }
        }
    }
});

Vue.component('train-query-contents', {
    template: '<section class="container">\
                   <train-query-parameter :from-station="from_station" :to-station="to_station" :train-date="train_date" @receive_input_true_data="receive_true_data"></train-query-parameter>\
               </section>',
    data: function() {
        return {
            from_station: '',
            to_station: '',
            train_date: ''
        }
    },
    methods: {
        receive_true_data: function(name, true_data) {
            switch (name) {
                case 'from_station': this.from_station = true_data; break;
                case 'to_station': this.to_station = true_data; break;
                case 'train_date': this.train_date = true_data; break;
            }

            if (this.from_station && this.to_station && this.train_date) {
                this.$emit('package_query_parameter', this.from_station, this.to_station, this.train_date);
            }
        }
    }
});

Vue.component('train-query-footer', {
    template: '<footer></footer>'
});