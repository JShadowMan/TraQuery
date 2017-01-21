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
    template: '<section class="train-query-parameter container"><form>' +
                  '<input-group type="text" label="FROM" name="from_station" ref="from_station" label-class="input-group-label" input-class="input-group-input" @receive_input_data="parse_input_data"></input-group>' +
                  '<input-group type="text" label="TO" name="to_station" ref="to_station" label-class="input-group-label" input-class="input-group-input" @receive_input_data="parse_input_data"></input-group>' +
                  '<input-group type="date" label="DATE" name="train_date" ref="train_date" label-class="input-group-label" input-class="input-group-input" @receive_input_data="parse_input_data"></input-group>' +
                  '<button class="train-query-submit widget-btn widget-btn-default" :class="button_style" :disabled="is_disable" @click.stop.prevent="query_train">Start</button>' +
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
                        // change progress
                        this.$root.event_bus.$emit('change-progress', 10, true);
                        // reset error
                        this.$root.event_bus.$emit('reset-error', response.key);
                    // station non-exists
                    } else {
                        // update sub-component status
                        sub_component.input_status = 'error';
                        // change progress
                        this.$root.event_bus.$emit('change-progress', -10, true);
                        // empty station code
                        this.$emit('receive_input_true_data', response.key, '');
                        // show error message
                        this.$root.event_bus.$emit('error-occurs', response.key, response.message, 'warning');
                    }
                }.bind(this));
            // is date data
            } else if (data.name === 'train_date') {
                var sub_component = this.$refs.train_date;
                var select_date = new Date(data.value.replace(/-/g, '/'));
                var current_date = new Date();

                var select_date_timestamp = select_date.getTime() / 1000;
                var current_date_timestamp = current_date.getTime() / 1000;

                if ((current_date_timestamp - select_date_timestamp < 86400)
                    || (select_date_timestamp > current_date_timestamp)) {
                    // change input status
                    sub_component.input_status = 'success';
                    // update train data
                    this.$emit('receive_input_true_data', 'train_date', data.value);
                    // change progress
                    this.$root.event_bus.$emit('change-progress', 10, true);
                } else {
                    // update train date to empty
                    this.$emit('receive_input_true_data', data.name, '');
                    // update input status
                    sub_component.input_status = 'error';
                    // change progress
                    this.$root.event_bus.$emit('change-progress', -10, true);
                }
            }
        },
        query_train: function() {
            if (this.fromStation && this.toStation && this.trainDate) {
                // change progress
                this.$root.event_bus.$emit('change-progress', 3, true);
                // change progress
                this.$root.event_bus.$emit('trigger-query-animation');
                // reset response
                this.$root.event_bus.$emit('reset-response');
                // WebSocket send request
                this.$root.socket.emit('request.train.list', {
                    from: this.fromStation,
                    to: this.toStation,
                    date: this.trainDate,
                    ts: (new Date()).getTime()
                });
            } else {
                alert('Hey Guy, too young, too simple, sometimes native')
            }
        }
    }
});

Vue.component('error-info', {
    template: '<transition name="fade"><section class="error-message" :class="error_class" v-if="error !== \'\'"><p>{{ error }}</p></section></transition>',
    props: ['error', 'level'],
    computed: {
        'error_class': function() {
            return 'error-level-' + (this.level ? this.level : 'default');
        }
    }
});

Vue.component('query-progress-animation', {
    template: '<transition name="query-animation"><section v-if="show" class="container"></section></transition>',
    props: ['show']
});

Vue.component('train-list', {
    // here hidden train code list
    // <ul class="train-list" v-if="false">
    template: '<transition name="fade">\
                   <section class="container train-list-container" v-if="count">\
                       <p class="train-count">Total {{ count }} {{ train_word }}</p>\
                       <ul class="train-list" v-if="false">\
                           <li v-for="train_code in list" class="train-list-item" :id="\'_\' + train_code">{{ train_code }}</li>\
                       </ul>\
                   </section>\
               </transition>',
    props: {
        count: {
            required: true,
            type: Number
        },
        list: {
            required: true,
            type: Array
        }
    },
    computed: {
        train_word: function() {
            return 'Train' + (this.count == 1 ? '' : 's');
        }
    }
});

Vue.component('train-profile', {
    template: '<tr>\
                   <td class="train-profile-item">{{ profile.train_code }}</td>\
                   <td class="train-profile-item">{{ profile.start_station[0] }}</td>\
                   <td class="train-profile-item">{{ profile.end_station[0] }}</td>\
                   <td class="train-profile-item">{{ profile.start_time }}</td>\
                   <td class="train-profile-item">{{ profile.arrive_time }}</td>\
                   <td class="train-profile-item">{{ profile.total_time }}</td>\
                   <td v-if="status_tag === \'button\'" class="train-profile-item"><button class="widget-btn widget-btn-default" :class="{ \'widget-btn-disabled\': profile.available }" :disabled="profile.available" title="Already available and does not need to query">Check</button></td>\
                   <td v-else class="train-profile-item">{{ profile.train_status }}</td>\
               </tr>',
    props: [ 'profile', 'status_tag' ]
});

Vue.component('train-query-result', {
    template: '<section class="container"><transition-group name="down-fade" tag="table" class="train-query-result-container">\
                      <train-profile v-if="trains.length" :profile="train_title" key="train_table_title" :status_tag="\'text\'"></train-profile>\
                      <train-profile v-for="train in trains" :profile="train" :key="train.train_code" :status_tag="\'button\'"></train-profile>\
               </transition-group></section>',
    data: function() {
        return {
            train_title: {
                train_code: 'Train Code',
                start_station: [ 'Start Station' ],
                end_station: [ 'End Station' ],
                start_time: 'Start Time',
                arrive_time: 'Arrive Time',
                total_time: 'Total Time',
                train_status: 'Status'
            }
        }
    },
    props: ['trains']
});

Vue.component('train-query-contents', {
    template: '<section class="train-query-contents">\
                   <train-query-parameter :from-station="from_station" :to-station="to_station" :train-date="train_date" @receive_input_true_data="receive_true_data"></train-query-parameter>\
                   <error-info :error="error_message" :level="error_level"></error-info>\
                   <query-progress-animation :show="show_progress"></query-progress-animation>\
                   <train-list :count="response_train_count" :list="response_train_list"></train-list>\
                   <train-query-result :trains="response_train_profile"></train-query-result>\
               </section>',
    data: function() {
        return {
            from_station: '',
            to_station: '',
            train_date: '',
            error_message: '',
            error_level: '',
            show_progress: false,
            error_trigger: null,
            response_train_count: 0,
            response_train_list: [],
            response_train_profile: []
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
    },
    created: function() {
        // receive train count
        this.$root.socket.on('response.train.count', function(message) {
            this.response_train_count = message.count;
        }.bind(this));
        // receive train list
        this.$root.socket.on('response.train.list', function(message) {
            this.response_train_list = message.list;
        }.bind(this));
        // receive train progress
        this.$root.socket.on('response.train.query.progress', function(message) {
            if (message.status === false) {
                // reset progress
                this.$root.event_bus.$emit('change-progress', 0);
                // trigger error
                this.$root.event_bus.$emit('error-occurs', 'socket', message.message);
            }
            if (message.progress === 100) {
                if (this.response_train_profile.length == 0) {
                    this.$root.event_bus.$emit('error-occurs', 'socket', 'Empty Trains')
                }

                // If increase to 100, then the element is gone directly
                this.$root.event_bus.$emit('change-progress', 99.999);
                // after increase to 100
                setTimeout(function() {
                    this.$root.event_bus.$emit('change-progress', 100);
                }.bind(this), 1000);
            } else if (message.progress == 0) {
                this.$root.event_bus.$emit('change-progress', 2, true);
            }
        }.bind(this));
        // receive each train profile
        this.$root.socket.on('response.train.profile', function(message) {
            this.response_train_profile.push(message)
        }.bind(this));
        // receive error message
        this.$root.event_bus.$on('error-occurs', function(trigger, error, error_level) {
            this.error_trigger = trigger;
            this.error_message = error;
        }.bind(this));
        // reset error
        this.$root.event_bus.$on('reset-error', function(trigger) {
            if (trigger && trigger === this.error_trigger) {
                this.error_message = '';
                this.error_level = '';
                this.error_trigger = '';
            }
        }.bind(this));
        // start query animation
        this.$root.event_bus.$on('trigger-query-animation', function() {
            this.show_progress = !this.show_progress;
        }.bind(this));
        // reset response
        this.$root.event_bus.$on('reset-response', function() {
            this.response_train_profile = [];
            this.response_train_count = 0;
            this.response_train_list = [];
        }.bind(this));
    }
});

Vue.component('train-query-footer', {
    template: '<footer></footer>'
});