/**
 * Mongolian locale for moment.js
 * Custom locale configuration for MagicMirror² Mongolian Language Pack
 */

(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory() :
    typeof define === 'function' && define.amd ? define(factory) :
    factory()
}(this, (function () { 'use strict';

    // Mongolian day names
    var mn = {
        months: 'Нэгдүгээр сар_Хоёрдугаар сар_Гуравдугаар сар_Дөрөвдүгээр сар_Тавдугаар сар_Зургадугаар сар_Долдугаар сар_Наймдугаар сар_Есдүгээр сар_Аравдугаар сар_Арван нэгдүгээр сар_Арван хоёрдугаар сар'.split('_'),
        monthsShort: '1-р сар_2-р сар_3-р сар_4-р сар_5-р сар_6-р сар_7-р сар_8-р сар_9-р сар_10-р сар_11-р сар_12-р сар'.split('_'),
        weekdays: 'Даваа гараг_Мягмар гараг_Лхагва гараг_Пүрэв гараг_Баасан гараг_Бямба гараг_Ням гараг'.split('_'),
        weekdaysShort: 'Дав_Мяг_Лха_Пүр_Баа_Бям_Ням'.split('_'),
        weekdaysMin: 'Да_Мя_Лх_Пү_Ба_Бя_Ня'.split('_'),
        longDateFormat: {
            LT: 'HH:mm',
            LTS: 'HH:mm:ss',
            L: 'YYYY-MM-DD',
            LL: 'YYYY оны MMMM-ын DD',
            LLL: 'YYYY оны MMMM-ын DD HH:mm',
            LLLL: 'dddd, YYYY оны MMMM-ын DD HH:mm'
        },
        calendar: {
            sameDay: '[Өнөөдөр] LT',
            nextDay: '[Маргааш] LT',
            nextWeek: '[Ирэх] dddd LT',
            lastDay: '[Өчигдөр] LT',
            lastWeek: '[Өнгөрсөн] dddd LT',
            sameElse: 'L'
        },
        relativeTime: {
            future: '%s-д',
            past: '%s-н өмнө',
            s: 'хэдэн секунд',
            ss: '%d секунд',
            m: 'нэг минут',
            mm: '%d минут',
            h: 'нэг цаг',
            hh: '%d цаг',
            d: 'нэг өдөр',
            dd: '%d өдөр',
            M: 'нэг сар',
            MM: '%d сар',
            y: 'нэг жил',
            yy: '%d жил'
        },
        dayOfMonthOrdinalParse: /\d{1,2}-(дүгээр|дугаар|т|р)/,
        ordinal: function (number, period) {
            switch (period) {
                case 'd':
                case 'D':
                case 'DDD':
                    return number + '-дүгээр';
                case 'M':
                    return number + '-р сар';
                case 'w':
                case 'W':
                    return number + '-р долоо хоног';
                default:
                    return number;
            }
        },
        week: {
            dow: 1, // Monday is the first day of the week
            doy: 4  // The week that contains Jan 4th is the first week of the year
        }
    };

    // Register the locale
    if (typeof moment !== 'undefined') {
        moment.defineLocale('mn', mn);
        moment.locale('mn');
    }

    // Export for Node.js environments
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = mn;
    }

})));
