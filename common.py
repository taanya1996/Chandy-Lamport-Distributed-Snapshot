class Messages:
	def __init__(self, reqType, fromClient, markerId = ""):	
		self.reqType = reqType
		self.fromClient = fromClient
		self.markerId = markerId

class State:
	def __init__(self, reqType, fromClient, markerId, tokenState, channelState):
		self.reqType = reqType
		self.fromClient = fromClient
		self.markerId = markerId
		self.tokenState = tokenState
		self.channelState = channelState

class TrackChannels:

	def __init__(self, markerId):
		self.markerId = markerId

		self.tokenState = False
		
		self.listenToChannel = {}
		self.listenToChannel[1] = False
		self.listenToChannel[2] = False
		self.listenToChannel[3] = False
		self.listenToChannel[4] = False
		self.listenToChannel[5] = False

		self.channelMessages = {}
		self.channelMessages[1] = []
		self.channelMessages[2] = []
		self.channelMessages[3] = []
		self.channelMessages[4] = []
		self.channelMessages[5] = []

		self.recievedMarkers = []

		self.snapshotCount = 0
		self.recievedSnaps = {}