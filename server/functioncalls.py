import matplotlib.pyplot as plt
import numpy as np
import io
from collections import Counter
from matplotlib.ticker import FuncFormatter
import pandas as pd


csv = ""

def setcsv(inputcsv: str) -> str:
    global csv
    print(f"Setting CSV data, length: {len(inputcsv)}")
    csv = inputcsv
    return "CSV data stored"


def calculateMean(colName: str) -> float | str:
    data = getColumnFromCSV(csv, colName)
    try:
        numeric_data = [float(x) for x in data]
        return sum(numeric_data) / len(numeric_data)
    except (ValueError, TypeError):
        return f"Error: Column '{colName}' contains non-numeric values"


def calculateMedian(colName: str) -> float | str:
    data = getColumnFromCSV(csv, colName)
    try:
        numeric_data = [float(x) for x in data]
        numeric_data.sort()
        if len(numeric_data) % 2 == 0:
            return (
                numeric_data[len(numeric_data) // 2]
                + numeric_data[len(numeric_data) // 2 - 1]
            ) / 2
        else:
            return numeric_data[len(numeric_data) // 2]
    except (ValueError, TypeError):
        return f"Error: Column '{colName}' contains non-numeric values"


def calculateMode(colName: str) -> str:
    data = getColumnFromCSV(csv, colName)
    try:
        numeric_data = [float(x) for x in data]
        # Get frequency of each value
        frequencies = Counter(numeric_data)
        max_freq = max(frequencies.values())
        
        # Find all values that appear with maximum frequency
        modes = [x for x, freq in frequencies.items() if freq == max_freq]
        
        # Handle different cases
        if max_freq == 1:
            return "No mode - all values appear once"
        elif len(modes) == 1:
            return str(modes[0])
        else:
            return f"Multiple modes: {', '.join(str(m) for m in sorted(modes))}"
            
    except (ValueError, TypeError):
        return f"Error: Column '{colName}' contains non-numeric values"


def calculateVariance(colName: str) -> float | str:
    data = getColumnFromCSV(csv, colName)
    try:
        numeric_data = [float(x) for x in data]
        mean = sum(numeric_data) / len(numeric_data)
        return sum((x - mean) ** 2 for x in numeric_data) / len(numeric_data)
    except (ValueError, TypeError):
        return f"Error: Column '{colName}' contains non-numeric values"


def calculateStandardDeviation(colName: str) -> float | str:
    data = getColumnFromCSV(csv, colName)
    try:
        variance = calculateVariance(colName)
        return variance**0.5
    except (ValueError, TypeError):
        return f"Error: Column '{colName}' contains non-numeric values"


# likely delete lol
def graphDisplay(data: list) -> str:
    data.sort()
    plt.hist(data, bins=10, color="blue", edgecolor="black")
    plt.xlabel("Data")
    plt.ylabel("Frequency")
    plt.title("Histogram of Data")
    plt.show()
    return "Graph displayed"


def histoToImage(
    data: list,
    xaxis: str,
    yaxis: str,
    title: str,
    density: bool = False,
    normal_dist: bool = False,
    histobin: int = 10,
) -> bytes:
    def format_yaxis(y, _):
        if density:
            return y
        else:
            if int(y) == y:
                return str(int(y))
            return ""

    plt.clf()  # Clear any existing plots
    data.sort()
    plt.hist(
        data,
        bins=histobin,
        color=(33 / 255, 127 / 255, 85 / 255),
        edgecolor="#7ed3aa",
        density=density,
    )

    if normal_dist:
        mean = calculateMean(data)
        std_dev = calculateStandardDeviation(data)
        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = np.exp(-0.5 * ((x - mean) / std_dev) ** 2) / (std_dev * np.sqrt(2 * np.pi))
        plt.plot(x, p, color="#d62728", linewidth=2)

    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(title)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_yaxis))
    fig = plt.gcf()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close()  # Clean up the plot
    return buf.getvalue()


def piechartToImage(data: dict, title: str) -> bytes:
    plt.clf()  # Clear any existing plots
    labels = data.keys()
    sizes = data.values()
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(title)
    fig = plt.gcf()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close()  # Clean up the plot
    return buf.getvalue()


def scatterplotToImage(
    xdata: list,
    ydata: list,
    xaxis: str,
    yaxis: str,
    title: str,
    line_of_best_fit: bool = False,
) -> bytes:
    plt.clf()  # Clear any existing plots
    plt.scatter(xdata, ydata, color="#1f77b4")

    if line_of_best_fit:
        # Calculate line of best fit
        m, b = np.polyfit(xdata, ydata, 1)
        plt.plot(xdata, [m * x + b for x in xdata], color="#7ed3aa")

    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(title)
    fig = plt.gcf()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close()  # Clean up the plot
    return buf.getvalue()


def bargraphToImage(data: dict, xaxis: str, yaxis: str, title: str) -> bytes:
    plt.clf()  # Clear any existing plots
    labels = data.keys()
    values = data.values()
    plt.bar(labels, values, color=(33 / 255, 127 / 255, 85 / 255))
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(title)
    fig = plt.gcf()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close()  # Clean up the plot
    return buf.getvalue()


def plotgraphToImage(
    xdata: list,
    ydata: list,
    xaxis: str,
    yaxis: str,
    title: str,
    show_points: bool = False,
) -> bytes:
    plt.clf()  # Clear any existing plots
    plt.plot(xdata, ydata, color=(33 / 255, 127 / 255, 85 / 255))

    if show_points:
        plt.scatter(xdata, ydata, color="red")  # Add points on the graph

    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(title)
    fig = plt.gcf()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close()  # Clean up the plot
    return buf.getvalue()


def modedecimalplaces(data: list) -> int:
    def countdecimalplaces(number: float) -> int:
        if "." in str(number):
            return len(str(number).split(".")[1])
        else:
            return 0

    decimalplaces = [countdecimalplaces(number) for number in data]

    modedecimal = Counter(decimalplaces).most_common(1)[0][0]
    return modedecimal


def getFirstColumnFromCSV(csv_string: str) -> list:
    cleaned_csv_string = csv_string.rstrip(",")  # Remove trailing comma
    df = pd.read_csv(io.StringIO(cleaned_csv_string.replace("\\n", "\n")))
    return [
        float(x) if isinstance(x, (np.integer, np.floating)) else x
        for x in df[df.columns[0]].tolist()
    ]


def getFirstRowFromCSV(csv_string: str) -> list:
    try:
        rows = csv_string.strip().split("\n")
        headers = [header.strip("\r") for header in rows[0].split(",")]
        print(f"Extracted headers: {headers}")
        return headers
    except Exception as e:
        print(f"Error parsing CSV headers: {str(e)}")
        raise e


def getFirstDataRowFromCSV(csv_string: str) -> list:
    try:
        rows = csv_string.strip().split("\n")
        if len(rows) > 1:  # Ensure there is at least one data row
            first_data_row = [value.strip('\r') for value in rows[1].split(",")]
            print(f"Extracted first data row: {first_data_row}")
            return first_data_row
        else:
            print("No data rows found in the CSV.")
            return []
    except Exception as e:
        print(f"Error parsing CSV data rows: {str(e)}")
        raise e


def getColumnFromCSV(csv_string: str, col_name: str) -> list:
    cleaned_csv_string = csv_string.rstrip(",")  # Remove trailing comma
    df = pd.read_csv(io.StringIO(cleaned_csv_string.replace("\\n", "\n")))
    if col_name in df.columns:
        return [
            float(x) if isinstance(x, (np.integer, np.floating)) else x
            for x in df[col_name].tolist()
        ]
    else:
        raise ValueError(f"Column '{col_name}' not found in CSV")


def getRowFromCSV(csv_string: str, row_name: str) -> list:
    cleaned_csv_string = csv_string.rstrip(",")  # Remove trailing comma
    df = pd.read_csv(io.StringIO(cleaned_csv_string.replace("\\n", "\n")), index_col=0)
    if row_name in df.index:
        return [
            float(x) if isinstance(x, (np.integer, np.floating)) else x
            for x in df.loc[row_name].tolist()
        ]
    else:
        raise ValueError(f"Row '{row_name}' not found in CSV")

def countRowsInCSV(csv_string: str) -> int:
    cleaned_csv_string = csv_string.rstrip(",")  # Remove trailing comma
    df = pd.read_csv(io.StringIO(cleaned_csv_string.replace("\\n", "\n")))
    return len(df.index)

def organizeDataCount(data: list) -> dict:
    return dict(Counter(data))

def getColumnInfo(colName: str) -> str:
    """Get detailed information about a specific column in the CSV data"""
    cleaned_csv_string = csv.rstrip(",")
    df = pd.read_csv(io.StringIO(cleaned_csv_string.replace("\\n", "\n")))
    
    if colName in df.columns:
        col_data = df[colName]
        info = f"Column '{colName}' analysis:\n"
        info += f"- Data type: {col_data.dtype}\n"
        info += f"- Total values: {len(col_data)}\n"
        info += f"- Unique values: {len(col_data.unique())}\n"
        info += f"- Missing values: {col_data.isnull().sum()}\n"
        if pd.api.types.is_numeric_dtype(col_data):
            info += f"- Minimum value: {col_data.min()}\n"
            info += f"- Maximum value: {col_data.max()}\n"
            info += f"- Average value: {col_data.mean():.2f}\n"
        else:
            most_common = col_data.value_counts().head(3)
            info += "- Most common values:\n"
            for val, count in most_common.items():
                info += f"  * {val}: {count} times\n"
        return info
    return f"Column '{colName}' not found in the data"

def searchValue(query: str) -> str:
    """Search for a specific value across all columns in the CSV data"""
    cleaned_csv_string = csv.rstrip(",")
    df = pd.read_csv(io.StringIO(cleaned_csv_string.replace("\\n", "\n")))
    
    results = []
    for column in df.columns:
        matches = df[df[column].astype(str).str.contains(str(query), case=False, na=False)]
        if not matches.empty:
            unique_matches = matches[column].unique()
            match_preview = ', '.join([str(x) for x in unique_matches[:3]])
            if len(unique_matches) > 3:
                match_preview += f", ... and {len(unique_matches)-3} more"
            results.append(f"- Column '{column}': {len(matches)} matches found\n"
                         f"  Example matches: {match_preview}")
    
    if results:
        return f"Search results for '{query}':\n" + "\n".join(results)
    return f"No matches found for '{query}' in any column"

def searchRowDetails(colName: str, query: str, limit: int = 5) -> str:
    """Search for rows where a specific column contains the query and return detailed information"""
    cleaned_csv_string = csv.rstrip(",")
    df = pd.read_csv(io.StringIO(cleaned_csv_string.replace("\\n", "\n")))
    
    if colName not in df.columns:
        return f"Column '{colName}' not found in the data"
    
    matches = df[df[colName].astype(str).str.contains(str(query), case=False, na=False)]
    
    if matches.empty:
        return f"No matches found for '{query}' in column '{colName}'"
    
    total_matches = len(matches)
    matches = matches.head(limit)  # Only take the requested number of matches
    
    result = f"Found {total_matches} rows where {colName} contains '{query}':\n"
    if total_matches > limit:
        result += f"(Showing first {limit} matches)\n\n"
    else:
        result += "\n"
    
    for idx, row in matches.iterrows():
        result += f"Match #{idx+1}:\n"
        for col in df.columns:
            value = row[col]
            if pd.isna(value):
                value = "N/A"
            result += f"- {col}: {value}\n"
        result += "\n"
    
    return result
