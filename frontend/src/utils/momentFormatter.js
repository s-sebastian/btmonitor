import moment from 'moment'
import momentDurationFormat from 'moment-duration-format'

//export const dateTimeSeconds = date => moment(date).format('YYYY-MM-DD HH:mm:ssZ')
export const dateTimeSeconds = date => moment(date).format('YYYY-MM-DD HH:mm:ss')
export const diffSeconds = date => moment().diff(date, 'seconds')
export const timeFromNow = time => moment(time).fromNow()
export const durationHours = time => moment.duration(time).asHours().toFixed(2)
export const durationSeconds = time => moment.duration(time).asSeconds()
export const durationUptime = duration => moment.duration(durationSeconds(duration), 'seconds').format('d[d], h[h]:mm[m]', {trim: false})
export const durationHumanize = duration => moment.duration(parseFloat(duration), 'seconds').format('d[d]-h[h]:mm[m]:ss[s].SSS', {trim: false})
export const dateTimeFormat = (date, format) => moment(date).format(format)
export const subtractMonth = (date) => moment(date).subtract(1, 'months')
