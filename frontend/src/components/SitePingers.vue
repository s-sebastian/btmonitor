<template>
  <div>
    <b-container v-if="!loading && !isStale && !offline" fluid class="text-center text-muted">
      <b-row>
        <b-col md="12" class="p-0 fixed-top">
          <b-progress
            :value="progressCount"
            :max="progressMax"
            height="2px"
            variant="warning">
          </b-progress>
        </b-col>
      </b-row>
    </b-container>
    <b-container v-if="!loading" class="text-center text-muted">
      <b-row>
        <b-col md="12">
          <b-alert v-if="isStale && !offline" variant="danger" show>
            <font-awesome-icon icon="exclamation-triangle"/>
            Stale data, last update {{ staleTime }}!
          </b-alert>
          <b-alert v-else-if="offline" variant="danger" show>
            <font-awesome-icon icon="exclamation-triangle"/>
            Failed to fetch data!
          </b-alert>
          <b-alert v-else variant="light" show class="mb-0">
          <small>Latest results from {{ lastUpdate }}</small>
          </b-alert>
        </b-col>
      </b-row>
      <b-row>
        <b-col md="12">
          <b-card-group deck class="mb-4">
            <b-card :border-variant="statusClass">
              <p class="card-text">
                <font-awesome-icon icon="power-off"/>
                <strong> Status:</strong>
                <span :class="'text-' + statusClass"> {{ status }}</span>
              </p>
            </b-card>
            <b-card :border-variant="onlineClass">
              <p class="card-text">
                <font-awesome-icon icon="exchange-alt"/>
                <strong> Online:</strong>
                <span :class="'text-' + onlineClass"> {{ online }}</span>
              </p>
            </b-card>
            <b-card :border-variant="downSpeedClass">
              <p class="card-text">
                <font-awesome-icon icon="arrow-circle-down"/>
                <strong> Download:</strong>
                <span :class="'text-' + downSpeedClass"> {{ downSpeed }}</span>
              </p>
            </b-card>
            <b-card :border-variant="upSpeedClass">
              <p class="card-text">
                <font-awesome-icon icon="arrow-circle-up"/>
                <strong> Upload:</strong>
                <span :class="'text-' + upSpeedClass"> {{ upSpeed }}</span>
              </p>
            </b-card>
          </b-card-group>
        </b-col>
      </b-row>
      <b-row>
        <b-col md="12" class="mb-2">
          <b-card-group deck>
            <b-card no-body>
              <b-card-body>
                <p class="card-text">
                  <font-awesome-icon icon="history"/>
                  <strong> System uptime:</strong>
                  <span :class="'text-' + systemUptimeClass"> {{ systemUptime }}</span>
                </p>
              </b-card-body>
              <line-chart css-classes="chart-wrapper" :chart-data="systemUptimeData"/>
            </b-card>
            <b-card no-body>
              <b-card-body>
                <p class="card-text">
                  <font-awesome-icon icon="history"/>
                  <strong> Network uptime:</strong>
                  <span :class="'text-' + networkUptimeClass"> {{ networkUptime }}</span>
                </p>
              </b-card-body>
              <line-chart css-classes="chart-wrapper" :chart-data="networkUptimeData"/>
            </b-card>
          </b-card-group>
        </b-col>
      </b-row>
      <div v-if="!loadingDownTime" class="text-small">
        <b-row v-if="downTime.length > 0" v-for="(item, index) in downTime" :key="item.date">
          <b-col md="12" class="mt-2 text-center">
            Downtime for {{ item.date }}: {{ item.total }} (x{{ item.results.length }})
            <b-table
              v-if="item.results.length > 0"
              responsive
              small
              :items="item.results"
              :fields="fields"
              :table-class="['text-muted']"
              class="mt-4 text-left">
            </b-table>
            <div v-else-if="typeof item.detail !== 'undefined'" class="mt-2 mb-3">
              {{ item.detail }}
            </div>
            <div v-else class="mt-2 mb-3">
              No downtime for this month!
            </div>
          </b-col>
        </b-row>
        <b-row>
          <b-col v-if="!loadingDownTimeClick" md="12">
            <b-button
              @click="getDownTime(false)"
              :disabled="offline || noData >= 3"
              size="sm"
              variant="outline-warning"
              class="mb-4">
                Load previous month
            </b-button>
          </b-col>
          <b-col v-else md="12" class="mb-4 text-center">
            <font-awesome-icon icon="spinner" size="lg" spin/>
          </b-col>
        </b-row>
      </div>
    </b-container>
    <b-container v-else>
      <b-row>
        <b-col md="12" class="mt-4 mb-4 text-center">
          <font-awesome-icon icon="sync-alt" spin/>
        </b-col>
      </b-row>
    </b-container>
    <b-container v-if="downTime.length > 1" fluid class="px-0 pt-5 text-center text-muted">
      <b-row>
        <b-col md="12" class="fixed-bottom clear-history-bg">
          <b-button
            @click="clearDownTime()"
            :disabled="offline"
            size="sm"
            variant="danger"
            class="mt-2 mb-2">
              Clear history
          </b-button>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>

import { options } from '../config/prod.env'
import LineChart from './charts/LineChart'
import {
  dateTimeSeconds,
  diffSeconds,
  durationHours,
  durationHumanize,
  durationUptime,
  timeFromNow,
  dateTimeFormat,
  subtractMonth,
  } from '../utils/momentFormatter'

const { sitePingers, downtime } = options.urls

export default {
  name: 'SitePingers',
  components: {
    LineChart
  },
  data: () => {
    return {
      timeOut: 60,
      offline: false,
      loading: true,
      loadingDownTime: true,
      loadingDownTimeClick: false,
      month: null,
      sP: [],
      sP0: {},
      downTime: [],
      noData: 0,
      disableLoadButton: false,
      interval: null,
      refresh: 10000,
      systemUptimeData: [],
      networkUptimeData: [],
      fields: ['start', 'end', 'duration']
    }
  },
  computed: {
    status () {
      this.$emit('status', this.sP0.status)
      return this.sP0.status || 'Unknown'
    },
    online () {
      return this.sP0.online || 'Unknown'
    },
    downSpeed () {
      return this.sP0.down_sync || 'Unknown'
    },
    upSpeed () {
      return this.sP0.up_sync || 'Unknown'
    },
    systemUptime () {
      return durationUptime(this.sP0.system_uptime)
    },
    networkUptime () {
      return durationUptime(this.sP0.network_uptime)
    },
    onlineClass () {
      return this.sP0.online === true ? 'success' : 'danger'
    },
    statusClass () {
      return (this.sP0.status === 'Connected') ? 'success' : 'danger'
    },
    downSpeedClass () {
      const speed = this.convertToMb(this.downSpeed)
      return (speed >= 20 && speed < 40) ? 'warning' : (speed >= 40) ? 'success' : 'danger'
    },
    upSpeedClass () {
      const speed = this.convertToMb(this.upSpeed)
      return (speed >= 5 && speed < 10) ? 'warning' : (speed >= 10) ? 'success' : 'danger'
    },
    systemUptimeClass () {
      const uptime = durationHours(this.sP0.system_uptime)
      return (uptime != 0 && uptime < 1) ? 'warning' : (uptime >= 1) ? 'success' : 'danger'
    },
    networkUptimeClass () {
      const uptime = durationHours(this.sP0.network_uptime)
      return (uptime != 0 && uptime < 1) ? 'warning' : (uptime >= 1) ? 'success' : 'danger'
    },
    lastUpdate () {
      return dateTimeSeconds(this.sP0.created)
    },
    isStale () {
      return diffSeconds(this.sP0.created) > this.timeOut
    },
    staleTime () {
      return timeFromNow(this.sP0.created)
    },
    progressCount () {
      const diff = diffSeconds(this.sP0.created)
      return (Math.floor(diff / 10) * 10)
    },
    progressMax () {
      return 60 - (this.refresh / 1000)
    },
  },
  methods: {
    getSitePingers () {
      fetch(sitePingers)
      .then(res => {
        if (!res.ok) {
          throw new Error(res.statusText);
        }
        return res.json()
      })
      .then(data => {
        this.loading = false
        this.offline = false
        this.sP = data
        this.sP0 = this.sP.results[0]
        const {created, ...rest} = this.sP0
        if (diffSeconds(created) > this.timeOut) {
          for (let i in rest) {
              this.sP0[i] = 'Unknown'
          }
        }
        let uptimeLabels = [],
            systemUptimeData = [],
            networkUptimeData = []
        this.sP.results.reverse().forEach(({created, system_uptime, network_uptime}) => {
          uptimeLabels.push(created)
          systemUptimeData.push(durationHours(system_uptime))
          networkUptimeData.push(durationHours(network_uptime))
        })
        this.systemUptimeData = this.fillData(uptimeLabels, systemUptimeData)
        this.networkUptimeData = this.fillData(uptimeLabels, networkUptimeData)
      })
      .catch(err => {
        this.loading = false
        this.offline = true
        const {created, ...rest} = this.sP0
        for (let i in rest) {
          this.sP0[i] = 'Unknown'
        }
        console.log(`SitePingers: ${err.message}`)
      })
    },
    getDownTime (current=true) {
      let url = downtime
      if (!current) {
        this.loadingDownTimeClick = true
        this.month = this.month ? subtractMonth(this.month) : subtractMonth()
        url += `${dateTimeFormat(this.month, 'YYYY/MM')}/`
      }
      fetch(url)
      .then(res => {
        if (!res.ok) {
          throw new Error(res.statusText);
        }
        return res.json()
      })
      .then(data => {
        const {date, total, results} = data
        data.date = dateTimeFormat(date, 'MMM-YYYY')
        data.total = durationHumanize(total)
        if (typeof results !== 'undefined' && results.length > 0) {
          data.results = results.map(({start, end, duration}) => {
            return {
              start: dateTimeSeconds(start),
              end : dateTimeSeconds(end),
              duration: durationHumanize(duration)
            }
          })
        } else if (typeof data.detail !== 'undefined') {
          data.date = dateTimeFormat(this.month, 'MMM-YYYY')
          data.results = []
          this.noData += 1
        }
        if (current) {
          this.downTime[0] = data
        } else {
          this.downTime.push(data)
          this.loadingDownTimeClick = false
        }
        this.loadingDownTime = false
      })
      .catch(err => {
        this.loading = false
        this.loadingDownTimeClick = false
        this.offline = true
        console.log(`Downtimes: ${err.message}`)
      })
    },
    clearDownTime () {
      this.downTime = this.downTime.splice(0, 1)
      this.noData = 0
      this.month = null
    },
    fillData (labels, data) {
      return {
        labels,
        datasets: [
          {
            label: 'Hours',
            borderColor: '#e5eae9',
            backgroundColor: '#f2f4f4',
            fill: true,
            pointRadius: 0,
            data
          }
        ]
      }
    },
    convertToMb (value) {
      if (typeof value === 'undefined') {
        return null
      }
      let [speed, unit] = value.split(' ')
      if (typeof unit !== 'undefined') {
        unit = unit.toLowerCase()
        if (unit === 'kbps') {
          speed /= 1024
        }
      }
      return speed
    },
  },
  watch: {
    status () {
      document.title = `${this.status} - BT monitor tool`
    }
  },
  mounted () {
    this.getSitePingers(),
    this.getDownTime(),
    this.interval = setInterval(function () {
      this.getSitePingers()
      this.getDownTime()
    }.bind(this), this.refresh)
  },
  beforeDestroy () {
    clearInterval(this.interval)
  },
}
</script>

<style scoped>
.bg-gradient-danger {
  background: linear-gradient(to right, #ffbf96, #fe7096);
}
.bg-gradient-info {
  background: linear-gradient(to right, #90caf9, #047edf 99%);
}
.bg-gradient-success {
  background: linear-gradient(to right, #84d9d2, #07cdae);
}
.chart-wrapper {
  height: 70px;
}
.text-small {
  font-size: 80%;
  font-weight: 400;
}
.clear-history-bg {
  background: white;
}
</style>
