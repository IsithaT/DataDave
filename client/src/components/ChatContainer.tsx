import FileInput from './FileInput';
import ChatMessages from './ChatMessages';
import { useChat } from '../hooks/useChat';
import { config } from '../config';

export default function ChatContainer() {
    const { context, handleFileAnalysis, handleSendMessage } = useChat();

    return (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4">
                <div className="sticky top-8">
                    <FileInput onAnalysis={handleFileAnalysis} />
                </div>
            </div>
            <div className="lg:col-span-8">
                {context.csvContent ? (
                    <ChatMessages 
                        messages={context.messages} 
                        onSendMessage={handleSendMessage}
                    />
                ) : (
                    <div className="h-[600px] flex items-center justify-center text-excel-600 text-lg border-2 border-dashed border-excel-300 rounded-lg bg-white/50">
                        <div className="text-center px-4">
                            <h2 className="text-2xl font-bold mb-2">Welcome to {config.assistant.name}</h2>
                            <p>Upload a CSV file to start analyzing your data</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
