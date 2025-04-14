import asyncio
import random
import time
import numpy as np
import sounddevice as sd
import os

from agents import (
    Agent,
    function_tool,
)
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    VoicePipeline,
)
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from dotenv import load_dotenv

# Loading the .env variables from the .env file
load_dotenv()


@function_tool
def get_listing_count() -> str:
    """Get the current number of active listings on Apprise Marketplace."""
    # This would normally connect to your database - using mock data for demo
    return "There are currently 1,248 active listings on Apprise Marketplace."


@function_tool
def get_popular_locations() -> str:
    """Get the most popular locations on Apprise Marketplace."""
    # This would normally connect to your analytics system - using mock data for demo
    locations = ["New York City", "Miami", "Los Angeles", "Austin", "Chicago"]
    return f"The most popular locations on Apprise Marketplace are {', '.join(locations)}."


@function_tool
def get_booking_process() -> str:
    """Explain the booking process on Apprise Marketplace."""
    return """The booking process on Apprise Marketplace is simple:
1. Create an account or log in
2. Browse listings and select one you're interested in
3. Check availability on the calendar
4. Click 'Request to Book' and enter your details
5. Wait for host approval (usually within 24 hours)
6. Once approved, complete payment to confirm your booking"""


@function_tool
def get_host_requirements() -> str:
    """Explain the requirements to become a host on Apprise Marketplace."""
    return """To become a host on Apprise Marketplace, you need:
1. A verified account with complete profile
2. Clear photos and detailed description of your space
3. Availability calendar
4. Valid payment information
5. Compliance with local regulations for short-term rentals"""


@function_tool
def get_cancellation_policy() -> str:
    """Explain the cancellation policies on Apprise Marketplace."""
    return """Apprise Marketplace offers three cancellation policy options:
1. Flexible: Full refund if cancelled 24 hours before check-in
2. Moderate: Full refund if cancelled 5 days before check-in
3. Strict: 50% refund if cancelled 7 days before check-in, no refund after
The specific policy is set by each host and is clearly displayed on the listing page."""


@function_tool
def contact_support() -> str:
    """Provide information about contacting customer support."""
    return """You can contact Apprise Marketplace support through:
1. Email: support@apprisemarketplace.com
2. Phone: 1-800-APP-RISE (available 24/7)
3. Live chat on our website or mobile app
For urgent matters related to a current stay, please use the emergency support option in the app."""


booking_agent = Agent(
    name="Booking Specialist",
    handoff_description="A specialist for booking-related inquiries and issues.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. You specialize in helping with booking issues "
        "on Apprise Marketplace. Help with booking processes, cancellations, modifications, and refunds. "
        "Always maintain a helpful and understanding tone, especially when dealing with booking issues."
    ),
    model="gpt-4o-mini",
)

host_agent = Agent(
    name="Host Support",
    handoff_description="A specialist for host-related inquiries and account management.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. You specialize in helping hosts on Apprise Marketplace. "
        "Provide guidance on creating listings, managing bookings, optimizing profiles, handling guests, "
        "and setting up pricing and availability. Be encouraging and supportive of hosts' success."
    ),
    model="gpt-4o-mini",
)

technical_agent = Agent(
    name="Technical Support",
    handoff_description="A specialist for technical issues and account troubleshooting.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. You specialize in technical support for "
        "Apprise Marketplace users. Help with login issues, app functionality, payment processing problems, "
        "and general troubleshooting. Be patient and clear with instructions."
    ),
    model="gpt-4o-mini",
)

agent = Agent(
    name="Apprise Assistant",
    instructions=prompt_with_handoff_instructions(
        "You are the primary voice assistant for Apprise Marketplace, a platform where users can host and book "
        "listings similar to Airbnb. Be friendly, helpful, and concise in your responses. "
        "You should help users with general questions about the platform, how it works, and provide basic information. "
        "When users ask specific questions about bookings, handoff to the Booking Specialist. "
        "When users need help with hosting or listing management, handoff to the Host Support agent. "
        "For technical issues or account problems, handoff to the Technical Support agent. "
        "Always maintain the brand voice of Apprise Marketplace: helpful, trustworthy, and welcoming."
    ),
    model="gpt-4o-mini",
    handoffs=[booking_agent, host_agent, technical_agent],
    tools=[
        get_listing_count,
        get_popular_locations,
        get_booking_process,
        get_host_requirements,
        get_cancellation_policy,
        contact_support,
    ],
)

# Define audio parameters
SAMPLE_RATE = 24000
CHANNELS = 1
DTYPE = np.int16

# Voice activity detection parameters
SILENCE_THRESHOLD = 500  # Adjust based on your microphone and environment
SILENCE_DURATION = 1.5  # How many seconds of silence to wait before stopping recording
BUFFER_DURATION = 0.5  # Additional buffer time to record after silence


def generate_tone(frequency=440, duration=0.3, volume=0.5):
    """Generate a tone to signal when to speak."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    tone = np.sin(2 * np.pi * frequency * t) * volume
    audio = np.array(tone * 32767, dtype=DTYPE)
    return audio


def play_tone():
    """Play a tone to signal the user to speak."""
    tone = generate_tone(frequency=880, duration=0.2)  # Higher frequency, shorter duration
    sd.play(tone, SAMPLE_RATE)
    sd.wait()


async def record_until_silence():
    """Record audio until silence is detected."""
    print("Listening... Speak now (will stop after silence)")

    # Play tone to signal user to speak
    play_tone()

    # Buffer to hold audio chunks
    chunks = []

    # Tracking variables for silence detection
    silent_frames = 0
    required_silent_frames = int(SILENCE_DURATION * SAMPLE_RATE / 1024)  # 1024 is frames per buffer
    buffer_frames = int(BUFFER_DURATION * SAMPLE_RATE / 1024)

    # Stream parameters
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        blocksize=1024
    )

    recording = False
    with stream:
        print("Recording started. Waiting for speech...")
        while True:
            # Read audio chunk
            data, overflowed = stream.read(1024)
            if overflowed:
                print("Warning: Audio buffer overflowed")

            # Calculate volume using absolute values
            volume = np.mean(np.abs(data))

            # Start recording when volume exceeds threshold
            if not recording and volume > SILENCE_THRESHOLD:
                recording = True
                print("Speech detected, recording...")

            # Add data to chunks if we're recording
            if recording:
                chunks.append(data.copy())

                # Check for silence to stop recording
                if volume < SILENCE_THRESHOLD:
                    silent_frames += 1
                    if silent_frames >= required_silent_frames:
                        # Add buffer frames after silence
                        for _ in range(buffer_frames):
                            data, _ = stream.read(1024)
                            chunks.append(data.copy())
                        break
                else:
                    silent_frames = 0

    if not chunks:
        print("No speech detected")
        return np.zeros(1024, dtype=DTYPE)

    # Combine all audio chunks
    audio_data = np.concatenate(chunks)
    print(f"Recording stopped. Captured {len(audio_data) / SAMPLE_RATE:.1f} seconds of audio")
    return audio_data


async def play_audio_stream(result):
    """Play the response audio stream."""
    # Create an audio player
    player = sd.OutputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE)
    player.start()

    print("Apprise Assistant is responding...")

    # Play the audio stream as it comes in
    async for event in result.stream():
        if event.type == "voice_stream_event_audio":
            player.write(event.data)

    player.stop()
    player.close()


async def main():
    # Clear screen for better user experience
    os.system('cls' if os.name == 'nt' else 'clear')

    # Display welcome banner
    print("=" * 60)
    print("           APPRISE MARKETPLACE VOICE ASSISTANT           ")
    print("=" * 60)
    print("Your virtual customer service agent for Apprise Marketplace")
    print("Ask about listings, bookings, hosting, or technical support")
    print("=" * 60)

    # Create the voice pipeline with the workflow
    pipeline = VoicePipeline(
        workflow=SingleAgentVoiceWorkflow(agent)
    )

    print("Apprise Assistant is ready to help you.")
    print("Starting conversation. Press Ctrl+C to exit.")

    try:
        # Initial greeting
        greeting = "Welcome to Apprise Marketplace customer support. How can I help you today?"
        print(f"\nAssistant: {greeting}")

        while True:
            # Record audio until silence is detected
            audio_data = await record_until_silence()

            if len(audio_data) <= 1024:  # No significant audio captured
                print("No speech detected. Please try again.")
                continue

            # Create a buffer with the recorded audio
            buffer = audio_data.flatten()
            audio_input = AudioInput(buffer=buffer)

            try:
                # Process the audio with the pipeline
                result = await pipeline.run(audio_input)

                # Play the response
                await play_audio_stream(result)
            except Exception as e:
                print(f"Error processing request: {e}")
                print("Let's try again.")

            # Small pause between conversation turns
            print("\nReady for your next question...")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nThank you for using Apprise Marketplace Voice Assistant. Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())