// Smart Agriculture and Rural Tech - Main JS Orchestrator

document.addEventListener('DOMContentLoaded', function() {
    // 1. Sidebar responsiveness toggler
    const sidebar = document.getElementById('sidebar');
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    
    if (sidebarCollapse && sidebar) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    // 2. Dark Mode state loader and toggle action
    const themeToggle = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';

    if (currentTheme === 'dark') {
        document.body.classList.add('dark-theme');
        if (themeToggle) themeToggle.checked = true;
    }

    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
            }
        });
    }

    // 3. AI Voice Assistant Implementation (Kannada & English)
    const voiceBtn = document.getElementById('voiceBtn');
    const voiceStatus = document.getElementById('voiceStatus');
    const voiceWave = document.getElementById('voiceWave');
    const assistantLang = document.getElementById('assistantLang'); // HTML selector: 'kn-IN' or 'en-US'
    
    let recognition = null;
    let isListening = false;
    
    // Check Speech Recognition capability
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onstart = function() {
            isListening = true;
            if (voiceStatus) voiceStatus.innerText = "Listening... / ಆಲಿಸಲಾಗುತ್ತಿದೆ...";
            if (voiceWave) voiceWave.classList.add('active');
            if (voiceBtn) voiceBtn.classList.replace('btn-outline-agri', 'btn-danger');
        };
        
        recognition.onend = function() {
            isListening = false;
            if (voiceWave) voiceWave.classList.remove('active');
            if (voiceBtn) voiceBtn.classList.replace('btn-danger', 'btn-outline-agri');
            if (voiceStatus) voiceStatus.innerText = "Click Microphone to speak";
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            console.log("Voice Input: ", transcript);
            if (voiceStatus) voiceStatus.innerText = `You said: "${transcript}"`;
            
            // Dispatch recognized voice transcript command to Python Backend for classification
            dispatchVoiceCommand(transcript);
        };
        
        recognition.onerror = function(event) {
            console.error("Speech Recognition Error: ", event.error);
            if (voiceStatus) voiceStatus.innerText = "Voice error. Try again.";
        };
        
        if (voiceBtn) {
            voiceBtn.addEventListener('click', function() {
                if (isListening) {
                    recognition.stop();
                } else {
                    // Set lang from selection (default Kannada)
                    recognition.lang = assistantLang ? assistantLang.value : 'kn-IN';
                    recognition.start();
                }
            });
        }
    } else {
        if (voiceStatus) voiceStatus.innerText = "Web Speech API is not supported in this browser.";
        if (voiceBtn) voiceBtn.style.display = 'none';
    }
    
    // Send Command to API
    function dispatchVoiceCommand(text) {
        fetch('/api/voice_assist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: text })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Voice Response: ", data);
            
            // Determine response language voice output
            const langCode = assistantLang ? assistantLang.value : 'kn-IN';
            const speakText = (langCode === 'kn-IN') ? data.kannada : data.english;
            
            // Use Web Speech Synthesis to talk back
            speakFeedback(speakText, langCode);
            
            if (voiceStatus) voiceStatus.innerText = speakText;
            
            // If redirect route target received, route user after a 1.8 second speech delay
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 2000);
            }
        })
        .catch(err => {
            console.error("Voice assist fetch error: ", err);
        });
    }
    
    // Text-To-Speech Synthesis helper
    function speakFeedback(text, lang) {
        if ('speechSynthesis' in window) {
            // Cancel active speech to prevent overlap
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = lang;
            
            // Look for matching browser voices
            const voices = window.speechSynthesis.getVoices();
            let voiceMatch = null;
            
            if (lang.startsWith('kn')) {
                voiceMatch = voices.find(v => v.lang.includes('kn') || v.lang.includes('IN'));
            } else {
                voiceMatch = voices.find(v => v.lang.includes('en'));
            }
            
            if (voiceMatch) utterance.voice = voiceMatch;
            
            window.speechSynthesis.speak(utterance);
        }
    }
    
    // Load voices in browser buffer
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => {};
    }
});
