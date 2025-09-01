import axios from 'axios';
import { store } from '../store';
import { logout, refreshToken, selectToken, selectRefreshToken } from '../store/authSlice';

// Create axios instance - use Ingress hostname
const api = axios.create({
    baseURL: 'http://event-booking.local',
    timeout: 30000, // Increased timeout for all API calls
});

// Debug log to confirm timeout settings
console.log('Frontend API timeout set to:', api.defaults.timeout);

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const state = store.getState();
        const token = selectToken(state);

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // If error is 401 and we haven't already tried to refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const state = store.getState();
            const refreshTokenValue = selectRefreshToken(state);

            if (refreshTokenValue) {
                try {
                    // Try to refresh the token
                    await store.dispatch(refreshToken(refreshTokenValue)).unwrap();

                    // Get the new token
                    const newState = store.getState();
                    const newToken = selectToken(newState);

                    // Retry the original request with new token
                    originalRequest.headers.Authorization = `Bearer ${newToken}`;
                    return api(originalRequest);
                } catch (refreshError) {
                    // If refresh fails, logout
                    store.dispatch(logout());
                    return Promise.reject(refreshError);
                }
            } else {
                // No refresh token, logout
                store.dispatch(logout());
            }
        }

        return Promise.reject(error);
    }
);

// Export the configured axios instance
export default api;

// Export individual service APIs - use correct service paths
export const authAPI = axios.create({
    baseURL: 'http://event-booking.local/auth',
    timeout: 20000, // Increased timeout for auth processing
});

export const catalogAPI = axios.create({
    baseURL: 'http://event-booking.local/catalog',
    timeout: 20000, // Increased timeout for catalog operations
});

export const bookingAPI = axios.create({
    baseURL: 'http://event-booking.local/booking',
    timeout: 30000, // Increased timeout for booking processing
});

// Debug log to confirm booking API timeout settings
console.log('Booking API timeout set to:', bookingAPI.defaults.timeout);

export const paymentAPI = axios.create({
    baseURL: 'http://event-booking.local/payment',
    timeout: 15000, // Increased timeout for payment processing
});

// Add interceptors to all service APIs
[authAPI, catalogAPI, bookingAPI, paymentAPI].forEach(serviceAPI => {
    // Request interceptor
    serviceAPI.interceptors.request.use(
        (config) => {
            const state = store.getState();
            const token = selectToken(state);

            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }

            return config;
        },
        (error) => {
            return Promise.reject(error);
        }
    );

    // Response interceptor
    serviceAPI.interceptors.response.use(
        (response) => {
            return response;
        },
        async (error) => {
            const originalRequest = error.config;

            if (error.response?.status === 401 && !originalRequest._retry) {
                originalRequest._retry = true;

                const state = store.getState();
                const refreshTokenValue = selectRefreshToken(state);

                if (refreshTokenValue) {
                    try {
                        await store.dispatch(refreshToken(refreshTokenValue)).unwrap();

                        const newState = store.getState();
                        const newToken = selectToken(newState);

                        originalRequest.headers.Authorization = `Bearer ${newToken}`;
                        return serviceAPI(originalRequest);
                    } catch (refreshError) {
                        store.dispatch(logout());
                        return Promise.reject(refreshError);
                    }
                } else {
                    store.dispatch(logout());
                }
            }

            return Promise.reject(error);
        }
    );
});
