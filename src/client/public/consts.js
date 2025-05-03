/**
 * The domain where the application is hosted.
 * @type {string}
 */
const DOMAIN = 'localhost';

/**
 * The port on which the application is served.
 * @type {string}
 */
const PORT = '8000';

/**
 * Constructs the full host URL using the domain and port.
 * @type {string}
 */
const HOST = `http://${DOMAIN}:${PORT}`;

window.CONSTS = {
  DOMAIN: DOMAIN,
  PORT: PORT,
  HOST: HOST,
};