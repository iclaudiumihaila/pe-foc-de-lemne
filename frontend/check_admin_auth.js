// Check admin authentication status
const token = localStorage.getItem('auth_access_token');
const user = localStorage.getItem('auth_user');

console.log('Admin token exists:', \!\!token);
if (token) {
    console.log('Token (first 20 chars):', token.substring(0, 20) + '...');
}

if (user) {
    try {
        const userData = JSON.parse(user);
        console.log('User data:', userData);
    } catch (e) {
        console.log('User data is not valid JSON:', user);
    }
} else {
    console.log('No user data found');
}

console.log('\nAll auth-related localStorage keys:');
for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key.includes('auth') || key.includes('token') || key.includes('user')) {
        console.log(`- ${key}:`, localStorage.getItem(key).substring(0, 50) + '...');
    }
}
EOF < /dev/null