<template>
<b-container v-if="!loading" class="text-center text-muted">
 <b-row>
    <b-col md="12">
      <b-alert v-if="isStale && !noConn" variant="danger" show>
        <font-awesome-icon icon="exclamation-triangle"/>
        Stale data, last update {{ staleTime }}!
      </b-alert>
      <b-alert v-else-if="noConn" variant="danger" show>
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
    <b-col md="12">
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
  <div v-if="isDownTime" class="text-small">
  <b-row>
    <b-col md="12" class="mt-4 text-center">
      Downtime for this month so far (x{{ downTime.count  }}): {{ downTime.total }}
    </b-col>
  </b-row>
  <b-row>
    <b-col md="12" class="mt-4 text-left">
      <b-table responsive small :items="downTime.results" :fields="fields"></b-table>
    </b-col>
  </b-row>
  </div>
  <b-row v-else-if="!noConn" class="text-small">
    <b-col md="12" class="mt-4 mb-4 text-center">
      No downtime for this month so far
    </b-col>
  </b-row>
</b-container>
<b-container v-else>
  <b-row>
    <b-col md="12" class="mt-4 mb-4 text-center">
      <font-awesome-icon icon="sync-alt" spin/>
    </b-col>
  </b-row>
</b-container>
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
  timeFromNow
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
      noConnInit: false,
      noConn: false,
      loading: true,
      sP: [],
      sP0: {},
      isDownTime: false,
      downTime: [],
      showFaults: false,
      interval: null,
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
      return (speed >= 40 && speed < 60) ? 'warning' : (speed >= 60) ? 'success' : 'danger'
    },
    upSpeedClass () {
      const speed = this.convertToMb(this.upSpeed)
      return (speed >= 10 && speed < 20) ? 'warning' : (speed >= 20) ? 'success' : 'danger'
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
    }
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
        this.noConn = false
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
        this.noConn = true
        const {created, ...rest} = this.sP0
        for (let i in rest) {
          this.sP0[i] = 'Unknown'
        }
        console.log(`SitePingers: ${err.message}`)
      })
    },
    getDownTime () {
      fetch(downtime)
      .then(res => {
        if (!res.ok) {
          throw new Error(res.statusText);
        }
        return res.json()
      })
      .then(data => {
        this.loading = false
        this.downTime = data
        const {total, results} = this.downTime
        if (typeof results !== 'undefined' && results.length > 0) {
          this.downTime.total = durationHumanize(total)
          this.downTime.count = results[0].id
          this.downTime.results.forEach(i => {
            i.start = dateTimeSeconds(i.start)
            i.end = dateTimeSeconds(i.end)
            i.duration = durationHumanize(i.duration)
          this.isDownTime = true
          })
        }
      })
      .catch(err => {
        this.loading = false
        this.noConn = true
        console.log(`Downtimes: ${err.message}`)
      })
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
    }.bind(this), 6000)
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
</style>
