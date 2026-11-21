import { Notify } from 'quasar';
import { register } from 'register-service-worker';
import { i18n } from 'src/boot/i18n';
import { markSwUpdated } from 'src/utils/chunkRecovery';

// The ready(), registered(), cached(), updatefound() and updated()
// events passes a ServiceWorkerRegistration instance in their arguments.
// ServiceWorkerRegistration: https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration

register(process.env.SERVICE_WORKER_FILE, {
  // The registrationOptions object will be passed as the second argument
  // to ServiceWorkerContainer.register()
  // https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerContainer/register#Parameter

  // registrationOptions: { scope: './' },

  ready (/* registration */) {
    // console.log('Service worker is active.')
  },

  registered (/* registration */) {
    // console.log('Service worker has been registered.')
  },

  cached (/* registration */) {
    // console.log('Content has been cached for offline use.')
  },

  updatefound (/* registration */) {
    // console.log('New content is downloading.')
  },

  updated (/* registration */) {
    markSwUpdated();
    Notify.create({
      message: i18n.global.t('pwa.updateAvailable'),
      color: 'primary',
      icon: 'system_update',
      position: 'bottom',
      timeout: 0,
      actions: [
        {
          label: i18n.global.t('pwa.reload'),
          color: 'white',
          handler: () => {
            window.location.reload();
          }
        },
        {
          icon: 'close',
          color: 'white',
          round: true,
          dense: true
        }
      ]
    });
  },

  offline () {
    // console.log('No internet connection found. App is running in offline mode.')
  },

  error (/* err */) {
    // console.error('Error during service worker registration:', err)
  },
});
