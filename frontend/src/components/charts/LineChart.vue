<script>

import { Line, mixins } from 'vue-chartjs'

const { reactiveProp } = mixins

export default {
  extends: Line,
  mixins: [reactiveProp],
  props: {
    chartData: {
      type: Array | Object,
      required: true,
    },
  },
  data () {
    return {
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {display: false},
        scales: {
          xAxes: [{
            display: false,
            scaleLabel: {
              display: false,
              labelString: 'Date'
            },
          }],
          yAxes: [{
            stacked: false,
            display: false,
            scaleLabel: {
              display: false,
              labelString: 'Price'
            },
            ticks: {
              //beginAtZero: true,
              suggestedMin: 0,
              suggestedMax: 24,
              reverse: false,
            }
          }]
        }
      }
    }
  },
  mounted () {
    this.renderChart(this.chartData, this.options)
  },
}

</script>
