// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getStorage, ref, getDownloadURL } from "firebase/storage";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBuOkFWW-Lh4_baQwx9-bk4lJ1ube93ehc",
  authDomain: "flutterproject-9fa77.firebaseapp.com",
  databaseURL: "https://flutterproject-9fa77-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "flutterproject-9fa77",
  storageBucket: "flutterproject-9fa77.appspot.com",
  messagingSenderId: "874531864475",
  appId: "1:874531864475:web:a3fb1ddbeeb628ba2f2b3e",
  measurementId: "G-7F5D4BJ93B"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const storage = getStorage(app);

export { storage };